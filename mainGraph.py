from langgraph.graph import StateGraph, END
import asyncio
from states.review_state import ReviewState
from merge_findings import merge_findings
from security_agent import security_agent
from style_agent import style_agent
from architecture_agent import architecture_agent
 


graph = StateGraph(ReviewState)
graph.add_node("security", security_agent)
graph.add_node("style", style_agent)
graph.add_node("architecture", architecture_agent)
graph.add_node("merge", merge_findings)



graph.add_edge("__start__", "security")
graph.add_edge("__start__", "style")
graph.add_edge("__start__", "architecture")

graph.add_edge("security", "merge")
graph.add_edge("style", "merge")
graph.add_edge("architecture", "merge")

graph.add_edge("merge", END)

diff_content="""diff --git a/order.py b/order.py
+def process_order(order_data):
+    if not order_data.get("email") or "@" not in order_data.get("email"):
+        raise ValueError("invalid email")
+    
+    with open("orders.log", "a") as f:
+        f.write(f"Order processed: {order_data}\\n")
+    
+    import smtplib
+    smtp = smtplib.SMTP("smtp.gmail.com", 587)
+    smtp.sendmail("orders@shop.com", order_data["email"], "Your order is confirmed")
"""

async def mainGraph (diff_content):
    app = graph.compile()
    result = await app.ainvoke({"diff": diff_content, "security_findings": [], "style_findings": [], "architecture_findings": [], "final_review": {}})
    print(result["final_review"])
    return result


if __name__ == "__main__":
    asyncio.run(mainGraph(diff_content)) 