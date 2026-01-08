"""ER Diagram tab for database entity-relationship visualization."""

from fasthtml.common import *
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
from fastflow import (
    FlowEditor, Edge, NodePalette, PaletteItem, TableNode,
)


def er_diagram_tab():
    """Database entity-relationship diagram."""
    return Div(
        Div(
            Aside(
                H3("Tables", style="margin: 0 0 16px 0; font-size: 14px;"),
                P("Drag tables to the canvas. Connect with relationship lines.",
                  style="font-size: 12px; color: #666; margin-bottom: 12px;"),
                NodePalette(
                    PaletteItem("table", "Table", icon="", inputs=1, outputs=1),
                    target_editor="er-flow"
                ),
                H4("Tips", style="margin: 20px 0 8px 0; font-size: 12px; color: #64748b;"),
                Div(
                    P("* Right-click table -> Add/Remove columns", style="margin: 0 0 4px 0; font-size: 11px; color: #64748b;"),
                    P("* Connect from any side (top, bottom, left, right)", style="margin: 0 0 4px 0; font-size: 11px; color: #64748b;"),
                    P("* Double-click to rename tables", style="margin: 0; font-size: 11px; color: #64748b;"),
                    style="padding: 10px; background: #f8fafc; border-radius: 6px; border: 1px solid #e2e8f0;"
                ),
                cls="sidebar"
            ),
            Main(
                FlowEditor(
                    # Users table
                    TableNode("users", x=50, y=50, label="users", columns=[
                        {"name": "id", "type": "bigint", "pk": True},
                        {"name": "name", "type": "varchar(255)"},
                        {"name": "email", "type": "varchar(255)"},
                        {"name": "created_at", "type": "timestamp"},
                    ]),
                    # Orders table
                    TableNode("orders", x=400, y=50, label="orders", columns=[
                        {"name": "id", "type": "bigint", "pk": True},
                        {"name": "user_id", "type": "bigint", "fk": "users.id"},
                        {"name": "total", "type": "decimal(10,2)"},
                        {"name": "status", "type": "varchar(50)"},
                    ]),
                    # Products table
                    TableNode("products", x=50, y=280, label="products", columns=[
                        {"name": "id", "type": "bigint", "pk": True},
                        {"name": "name", "type": "varchar(255)"},
                        {"name": "price", "type": "decimal(10,2)"},
                        {"name": "stock", "type": "int"},
                        {"name": "count", "type": "int"},
                    ]),
                    # Order Items table
                    TableNode("order_items", x=400, y=280, label="order_items", columns=[
                        {"name": "id", "type": "bigint", "pk": True},
                        {"name": "order_id", "type": "bigint", "fk": "orders.id"},
                        {"name": "product_id", "type": "bigint", "fk": "products.id"},
                        {"name": "quantity", "type": "int"},
                    ]),
                    # Relationships - demonstrating both horizontal and vertical connections
                    Edge(source="users", target="orders", relationship="1:N", router="er",
                         source_port="port_right", target_port="port_left"),  # horizontal
                    Edge(source="orders", target="order_items", relationship="1:N", router="er",
                         source_port="port_bottom", target_port="port_top"),  # vertical
                    Edge(source="products", target="order_items", relationship="1:N", router="er",
                         source_port="port_right", target_port="port_left"),  # horizontal
                    id="er-flow",
                    on_change="/flow/changed",
                ),
                cls="editor-main"
            ),
            cls="app-container"
        ),
        id="tab-er"
    )
