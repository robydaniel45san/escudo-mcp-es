"""Conector MCP de juguete: clima. Todas sus herramientas son limpias."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("clima")


@mcp.tool()
def clima_actual(ciudad: str) -> str:
    """Devuelve el clima actual de una ciudad."""
    return "soleado"


@mcp.tool()
def pronostico(ciudad: str, dias: int = 3) -> str:
    """Devuelve el pronóstico de los próximos días para una ciudad."""
    return "soleado"


if __name__ == "__main__":
    mcp.run()
