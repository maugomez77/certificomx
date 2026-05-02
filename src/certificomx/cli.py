import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

app = typer.Typer(help="CertificoMX — Trades certification & US job placement for Mexico")
console = Console()


def _get_store():
    """Return a simple httpx client pointed at the local API."""
    import httpx
    return httpx.Client(base_url="http://localhost:8000/api/v1", timeout=30)


@app.command()
def workers(
    trade: str = typer.Option(None, help="Filter by trade"),
    status: str = typer.Option(None, help="Filter by status"),
):
    """List registered workers."""
    params = {}
    if trade:
        params["trade"] = trade
    if status:
        params["status"] = status
    try:
        with _get_store() as client:
            data = client.get("/workers", params=params).json()
    except Exception as e:
        console.print(f"[red]API unavailable: {e}[/red]")
        return

    table = Table("ID", "Name", "Trade", "City", "English", "Experience", "Status", box=box.ROUNDED)
    for w in data:
        status_color = {"seeking": "yellow", "certified": "blue", "placed": "green", "inactive": "dim"}.get(w["status"], "white")
        table.add_row(
            str(w["id"]), w["name"], w["trade"], w.get("city", ""),
            w.get("english_level", "none"), f"{w.get('experience_years', 0)}y",
            f"[{status_color}]{w['status']}[/{status_color}]",
        )
    console.print(table)


@app.command()
def worker_add():
    """Register a new worker interactively."""
    console.print(Panel("[bold cyan]Registrar Trabajador / Register Worker[/bold cyan]"))
    name = typer.prompt("Nombre completo / Full name")
    phone = typer.prompt("Teléfono / Phone")
    trade = typer.prompt("Oficio / Trade (welding/electrical/automotive/plumbing/electronics/logistics/manufacturing)")
    city = typer.prompt("Ciudad / City")
    state = typer.prompt("Estado / State")
    experience = typer.prompt("Años de experiencia / Years of experience", default="0")
    english = typer.prompt("Nivel de inglés / English level (none/basic/intermediate/advanced)", default="none")

    payload = {
        "name": name, "phone": phone, "trade": trade,
        "city": city, "state": state,
        "experience_years": int(experience), "english_level": english,
    }
    try:
        with _get_store() as client:
            resp = client.post("/workers", json=payload)
            w = resp.json()
        console.print(f"[green]✓ Trabajador registrado con ID {w['id']}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def certifications(trade: str = typer.Option(None, help="Filter by trade")):
    """List available certifications."""
    params = {}
    if trade:
        params["trade"] = trade
    try:
        with _get_store() as client:
            data = client.get("/certifications", params=params).json()
    except Exception as e:
        console.print(f"[red]API unavailable: {e}[/red]")
        return

    table = Table("ID", "Code", "Name", "Trade", "Authority", "Level", "Hours", "Cost MXN", box=box.ROUNDED)
    for c in data:
        table.add_row(
            str(c["id"]), c["code"], c["name"], c["trade"],
            c["authority"], c["level"], str(c["duration_hours"]),
            f"${c['cost_mxn']:,.0f}",
        )
    console.print(table)


@app.command()
def jobs(trade: str = typer.Option(None, help="Filter by trade")):
    """Browse active job postings."""
    params = {"status": "active"}
    if trade:
        params["trade"] = trade
    try:
        with _get_store() as client:
            data = client.get("/jobs", params=params).json()
    except Exception as e:
        console.print(f"[red]API unavailable: {e}[/red]")
        return

    table = Table("ID", "Title", "Trade", "Location", "Salary USD/yr", "Visa", box=box.ROUNDED)
    for j in data:
        salary = f"${j['salary_usd_min']:,.0f}-${j['salary_usd_max']:,.0f}"
        visa = "[green]Yes[/green]" if j["visa_sponsored"] else "No"
        table.add_row(str(j["id"]), j["title"], j["trade"], j["location_type"], salary, visa)
    console.print(table)


@app.command()
def career_path(worker_id: int):
    """AI career path recommendation for a worker."""
    try:
        with _get_store() as client:
            result = client.post(f"/ai/career-path?worker_id={worker_id}").json()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return

    console.print(Panel(f"[bold]AI Career Path for Worker #{worker_id}[/bold]"))
    for i, path in enumerate(result.get("paths", []), 1):
        console.print(f"\n[bold cyan]Path {i}: {path.get('name')}[/bold cyan]")
        console.print(f"  Authority: {path.get('authority')} | US Equivalent: {path.get('us_equivalent')}")
        console.print(f"  Timeline: {path.get('timeline_months')} months | Salary: ${path.get('expected_salary_usd_min'):,}-${path.get('expected_salary_usd_max'):,}/yr")
        console.print(f"  Placement probability: [green]{path.get('placement_probability_pct')}%[/green]")
        for step in path.get("steps", []):
            console.print(f"    • {step}")
    console.print(f"\n[italic]{result.get('recommendation', '')}[/italic]")


@app.command()
def job_match(worker_id: int):
    """AI job matching for a worker."""
    try:
        with _get_store() as client:
            matches = client.post(f"/ai/job-match?worker_id={worker_id}").json()
            jobs_data = client.get("/jobs").json()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return

    jobs_by_id = {j["id"]: j for j in jobs_data}
    console.print(Panel(f"[bold]Top Job Matches for Worker #{worker_id}[/bold]"))
    for m in matches:
        job = jobs_by_id.get(m.get("job_id"), {})
        score = m.get("match_score", 0)
        color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        console.print(f"\n[{color}]{score}% match[/{color}] — {job.get('title', 'Job #' + str(m.get('job_id')))}")
        console.print(f"  {m.get('reasoning', '')}")


@app.command()
def market_intel():
    """Live market intelligence for nearshoring trades."""
    console.print("[dim]Fetching live market data...[/dim]")
    try:
        with _get_store() as client:
            data = client.get("/ai/market-intel").json()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return

    console.print(Panel("[bold]CertificoMX Market Intelligence Report[/bold]"))
    console.print("\n[bold cyan]Top Trades in Demand:[/bold cyan]")
    for t in data.get("top_trades", []):
        demand_color = "green" if t["demand"] == "high" else "yellow"
        console.print(f"  [{demand_color}]{t['trade']}[/{demand_color}] — ${t.get('avg_salary_usd', 0):,}/yr ({t['demand']} demand, {t.get('growth', '')})")

    console.print(f"\n[bold cyan]Outlook:[/bold cyan] {data.get('outlook', '')}")
    console.print(f"\n[bold cyan]Best Cities:[/bold cyan] {', '.join(data.get('best_cities', []))}")


@app.command()
def dashboard():
    """Platform KPI overview."""
    try:
        with _get_store() as client:
            data = client.get("/dashboard").json()
    except Exception as e:
        console.print(f"[red]API unavailable: {e}[/red]")
        return

    console.print(Panel("[bold]CertificoMX Dashboard[/bold]"))
    table = Table(box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_row("Total Workers", str(data["total_workers"]))
    table.add_row("Active (Seeking)", str(data["active_workers"]))
    table.add_row("Placed", str(data["placed_this_month"]))
    table.add_row("Active Jobs", str(data["active_jobs"]))
    table.add_row("Employers", str(data["total_employers"]))
    table.add_row("Applications", str(data["total_applications"]))
    table.add_row("Placement Rate", f"[green]{data['placement_rate']}%[/green]")
    console.print(table)

    if data.get("top_trades"):
        console.print("\n[bold]Top Trades:[/bold]")
        for t in data["top_trades"]:
            console.print(f"  • {t['trade']}: {t['count']} workers")


@app.command()
def serve(port: int = 8000, reload: bool = True):
    """Start the FastAPI server."""
    import uvicorn
    uvicorn.run("certificomx.api:app", host="0.0.0.0", port=port, reload=reload)


if __name__ == "__main__":
    app()
