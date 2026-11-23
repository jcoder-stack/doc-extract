"""第 3 课：订单 MCP Server

把第 2 课的三个工具搬进一个 MCP Server。之后任何支持 MCP 的 Agent
（Claude Code、Claude Desktop、Cursor、你自己写的客户端……）都能直接用。

运行方式（一般不用手动跑，由客户端启动它）：
    uv run 03_order_server.py

C# 对照：
    MCPServer(...)           ≈ builder.Services.AddMcpServer().WithStdioServerTransport()
    @mcp.tool()              ≈ [McpServerTool] 标在方法上
    raise ToolError(...)     ≈ 抛一个“业务异常”，消息会给到模型（类似 ABP 的 UserFriendlyException）
    Field(description=...)   ≈ [Description("...")] 标在参数上
    docstring                ≈ 方法上的 [Description]，模型看到的工具说明

⚠ stdio 模式下 stdout 是协议通道，千万不要 print()！要打日志请写到 stderr。
"""

import sys
from typing import Annotated

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

mcp = MCPServer(
    name="order-service",
    instructions="订单客服用的只读查询工具：查订单、查物流、按客户查订单号。",
)

# ---------- 假数据（和第 2 课一样，真实项目换成数据库或接口） ----------

ORDERS = [
    {"order_id": "1024", "customer": "上海星辰软件有限公司", "amount": 5000, "status": "待发货",
     "payment_status": "待确认：银行转账已提交，等待财务核对到账"},
    {"order_id": "1025", "customer": "上海星辰软件有限公司", "amount": 1280, "status": "已发货", "payment_status": "已支付"},
    {"order_id": "1026", "customer": "杭州云帆科技有限公司", "amount": 860, "status": "已完成", "payment_status": "已支付"},
]
SHIPMENTS = {
    "1025": {"carrier": "顺丰", "tracking_no": "SF1234567890", "location": "杭州转运中心，预计明天送达"},
    "1026": {"carrier": "中通", "tracking_no": "ZT9876543210", "location": "已签收"},
}

OrderId = Annotated[str, Field(description="订单号，例如 1024")]   # 类型别名，几个工具共用


# ---------- 工具：和第 2 课相比，不用再手写 JSON Schema 了 ----------

@mcp.tool()
def get_order(order_id: OrderId) -> dict:
    """按订单号查询订单详情：客户、金额、订单状态、支付状态。"""
    print(f"[order-service] get_order({order_id})", file=sys.stderr)   # 日志写 stderr
    order = next((o for o in ORDERS if o["order_id"] == order_id), None)
    if order is None:
        # 抛 ToolError → 结果标记 isError=true，这句话原样交给模型，让它自己纠正。
        # 抛其他异常（比如 ValueError）会被当成程序崩溃，模型只看到 "Error executing tool"，细节留在服务端日志。
        raise ToolError(f"找不到订单 {order_id}，请确认订单号，或先用 find_orders_by_customer 查询")
    return order


@mcp.tool()
def get_shipment(order_id: OrderId) -> dict:
    """按订单号查询物流信息。订单还没发货时会说明未发货。"""
    return SHIPMENTS.get(order_id, {"order_id": order_id, "shipped": False, "note": "还没有物流信息（未发货）"})


@mcp.tool()
def find_orders_by_customer(
    customer_name: Annotated[str, Field(description="客户名称，可以只写一部分，例如 星辰")],
) -> list[str]:
    """按客户名称（可以只写一部分）查询该客户的所有订单号。"""
    return [o["order_id"] for o in ORDERS if customer_name in o["customer"]]


# ---------- 资源：给“人或应用”挑选后放进上下文的只读数据（了解即可） ----------

@mcp.resource("orders://summary", name="订单概览", mime_type="text/plain")
def orders_summary() -> str:
    """所有订单的一行摘要。"""
    return "\n".join(f"{o['order_id']} {o['customer']} {o['status']}" for o in ORDERS)


if __name__ == "__main__":   # 相当于 C# 的 Main()：直接运行这个文件时才执行
    mcp.run()                # 默认 stdio 传输；换成 mcp.run("streamable-http") 就是 HTTP 服务
