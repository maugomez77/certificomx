"""Seed real Mexican trade certifications into CertificoMX."""
import asyncio
from .database import init_db, AsyncSessionLocal, CertificationDB
from sqlalchemy import select


CERTIFICATIONS = [
    # ── Welding / Soldadura ────────────────────────────────────────────────
    {
        "name": "Soldadura con Proceso SMAW Básico",
        "code": "EC0217",
        "trade": "welding",
        "authority": "CONOCER",
        "level": "basic",
        "duration_hours": 80,
        "cost_mxn": 1500,
        "passing_score": 70,
        "us_equivalent": "AWS D1.1 Structural Welding",
        "description_es": "Certificación CONOCER para soldadura con electrodo revestido (SMAW). Cubre preparación, ejecución y control de calidad de uniones soldadas.",
        "description_en": "CONOCER certification for shielded metal arc welding (SMAW). Covers preparation, execution, and quality control of welded joints.",
    },
    {
        "name": "Soldadura MIG/MAG (GMAW) Intermedio",
        "code": "EC0366",
        "trade": "welding",
        "authority": "CONOCER",
        "level": "intermediate",
        "duration_hours": 120,
        "cost_mxn": 2200,
        "passing_score": 75,
        "us_equivalent": "AWS D1.1 / AWS D1.2 GMAW Certified",
        "description_es": "Certificación para soldadura con gas inerte de metal (MIG/MAG). Incluye soldadura de acero al carbono, acero inoxidable y aluminio.",
        "description_en": "Certification for gas metal arc welding (MIG/MAG). Includes carbon steel, stainless steel, and aluminum welding.",
    },
    {
        "name": "Inspector de Soldadura NOM-STPS",
        "code": "NOM-027-STPS-2008",
        "trade": "welding",
        "authority": "STPS",
        "level": "advanced",
        "duration_hours": 160,
        "cost_mxn": 4500,
        "passing_score": 80,
        "us_equivalent": "AWS CWI (Certified Welding Inspector)",
        "description_es": "Certificación de inspector de soldadura bajo normativa STPS. Habilita para supervisar procesos de soldadura en planta y verificar cumplimiento NOM.",
        "description_en": "Welding inspector certification under STPS regulations. Qualifies for supervising welding processes and NOM compliance verification.",
    },
    # ── Electrical / Electricidad ──────────────────────────────────────────
    {
        "name": "Instalaciones Eléctricas Residenciales",
        "code": "EC0372",
        "trade": "electrical",
        "authority": "CONOCER",
        "level": "basic",
        "duration_hours": 60,
        "cost_mxn": 1200,
        "passing_score": 70,
        "us_equivalent": "IBEW Residential Electrician Apprentice",
        "description_es": "Certificación para instalación y mantenimiento de sistemas eléctricos residenciales conforme a NOM-001-SEDE-2012.",
        "description_en": "Certification for installation and maintenance of residential electrical systems per NOM-001-SEDE-2012.",
    },
    {
        "name": "Electricista Industrial NOM-001-SEDE",
        "code": "EC0440",
        "trade": "electrical",
        "authority": "CONOCER",
        "level": "intermediate",
        "duration_hours": 150,
        "cost_mxn": 3000,
        "passing_score": 75,
        "us_equivalent": "IBEW Journeyman Electrician",
        "description_es": "Certificación para instalaciones eléctricas industriales: tableros, motores, transformadores y sistemas de control, conforme NOM-001-SEDE.",
        "description_en": "Certification for industrial electrical installations: panels, motors, transformers, and control systems per NOM-001-SEDE.",
    },
    {
        "name": "Técnico en Automatización y PLC",
        "code": "EC0536",
        "trade": "electrical",
        "authority": "CONOCER",
        "level": "advanced",
        "duration_hours": 200,
        "cost_mxn": 5500,
        "passing_score": 80,
        "us_equivalent": "Allen Bradley PLC Technician / NFPA 70E",
        "description_es": "Certificación en programación y mantenimiento de PLC (Siemens, Allen Bradley), HMI y sistemas SCADA para industria manufacturera.",
        "description_en": "Certification in PLC programming and maintenance (Siemens, Allen Bradley), HMI, and SCADA systems for manufacturing.",
    },
    # ── Automotive / Automotriz ────────────────────────────────────────────
    {
        "name": "Mantenimiento y Reparación Automotriz Básico",
        "code": "EC0396",
        "trade": "automotive",
        "authority": "CONOCER",
        "level": "basic",
        "duration_hours": 80,
        "cost_mxn": 1800,
        "passing_score": 70,
        "us_equivalent": "ASE Entry Level (A Series)",
        "description_es": "Certificación básica para diagnóstico y mantenimiento preventivo de vehículos ligeros. Cubre motor, frenos, suspensión y sistema eléctrico básico.",
        "description_en": "Basic certification for diagnosis and preventive maintenance of light vehicles. Covers engine, brakes, suspension, and basic electrical system.",
    },
    {
        "name": "Técnico en Diagnóstico Electrónico Automotriz",
        "code": "EC0487",
        "trade": "automotive",
        "authority": "CONOCER",
        "level": "intermediate",
        "duration_hours": 120,
        "cost_mxn": 3200,
        "passing_score": 75,
        "us_equivalent": "ASE A6 / A8 Electrical & Electronic Systems",
        "description_es": "Diagnóstico electrónico con scanner OBD-II, programación de módulos ECU, análisis de sistemas CAN bus y diagnóstico de vehículos híbridos.",
        "description_en": "Electronic diagnostics with OBD-II scanner, ECU module programming, CAN bus system analysis, and hybrid vehicle diagnostics.",
    },
    {
        "name": "Técnico en Manufactura Automotriz Tier 1",
        "code": "CONALEP-AUTO-ADV",
        "trade": "automotive",
        "authority": "CONALEP",
        "level": "advanced",
        "duration_hours": 180,
        "cost_mxn": 4800,
        "passing_score": 80,
        "us_equivalent": "Toyota Production System / IATF 16949",
        "description_es": "Certificación para trabajar en líneas de ensamble automotriz Tier 1. Incluye manufactura esbelta, control de calidad IATF 16949 y seguridad en planta.",
        "description_en": "Certification to work in Tier 1 automotive assembly lines. Includes lean manufacturing, IATF 16949 quality control, and plant safety.",
    },
    # ── Plumbing / Plomería ───────────────────────────────────────────────
    {
        "name": "Instalación de Sistemas Hidrosanitarios",
        "code": "EC0289",
        "trade": "plumbing",
        "authority": "CONOCER",
        "level": "basic",
        "duration_hours": 60,
        "cost_mxn": 1100,
        "passing_score": 70,
        "us_equivalent": "UA Plumbers Apprentice (United Association)",
        "description_es": "Certificación para instalación de redes de agua potable, drenaje y gas natural en edificaciones residenciales y comerciales.",
        "description_en": "Certification for installation of potable water networks, drainage, and natural gas in residential and commercial buildings.",
    },
    {
        "name": "Plomero Industrial y Sistemas de Vapor",
        "code": "CONALEP-PLOM-INT",
        "trade": "plumbing",
        "authority": "CONALEP",
        "level": "intermediate",
        "duration_hours": 140,
        "cost_mxn": 2800,
        "passing_score": 75,
        "us_equivalent": "UA Journeyman Pipefitter",
        "description_es": "Instalación y mantenimiento de tuberías industriales, sistemas de vapor, aire comprimido y fluidos a presión en planta industrial.",
        "description_en": "Installation and maintenance of industrial piping, steam systems, compressed air, and pressure fluids in industrial plants.",
    },
    # ── Electronics / Electrónica ──────────────────────────────────────────
    {
        "name": "Técnico en Electrónica y Tarjetas de Circuito",
        "code": "EC0181",
        "trade": "electronics",
        "authority": "CONOCER",
        "level": "basic",
        "duration_hours": 90,
        "cost_mxn": 2000,
        "passing_score": 70,
        "us_equivalent": "IPC-A-610 Acceptability of Electronic Assemblies",
        "description_es": "Certificación para ensamble y reparación de tarjetas de circuito impreso (PCB). Cubre soldadura SMD, THT e inspección visual IPC.",
        "description_en": "Certification for PCB assembly and repair. Covers SMD and THT soldering and IPC visual inspection.",
    },
    {
        "name": "Inspector de Calidad Electrónica IPC",
        "code": "IPC-7711-7721",
        "trade": "electronics",
        "authority": "NOM",
        "level": "intermediate",
        "duration_hours": 120,
        "cost_mxn": 3500,
        "passing_score": 80,
        "us_equivalent": "IPC CIS (Certified IPC Specialist)",
        "description_es": "Certificación IPC para inspección, rework y reparación de ensambles electrónicos. Reconocida internacionalmente por fabricantes OEM.",
        "description_en": "IPC certification for inspection, rework, and repair of electronic assemblies. Internationally recognized by OEM manufacturers.",
    },
    {
        "name": "Técnico en Pruebas y Calibración de Equipos",
        "code": "EC0536-ADV",
        "trade": "electronics",
        "authority": "CONOCER",
        "level": "advanced",
        "duration_hours": 160,
        "cost_mxn": 4200,
        "passing_score": 80,
        "us_equivalent": "NIST-Traceable Calibration Technician",
        "description_es": "Calibración de instrumentos de medición eléctrica y electrónica conforme ISO/IEC 17025. Uso de multímetros, osciloscopios y analizadores.",
        "description_en": "Calibration of electrical and electronic measurement instruments per ISO/IEC 17025. Use of multimeters, oscilloscopes, and analyzers.",
    },
    # ── Logistics / Logística ─────────────────────────────────────────────
    {
        "name": "Operador de Montacargas Certificado",
        "code": "EC0271",
        "trade": "logistics",
        "authority": "CONOCER",
        "level": "basic",
        "duration_hours": 40,
        "cost_mxn": 900,
        "passing_score": 70,
        "us_equivalent": "OSHA Forklift Operator Certification",
        "description_es": "Certificación para operación segura de montacargas contrabalanceado, retráctil y de pasillo estrecho. Cumplimiento NOM-006-STPS.",
        "description_en": "Certification for safe operation of counterbalanced, reach, and narrow-aisle forklifts. NOM-006-STPS compliance.",
    },
    {
        "name": "Coordinador de Almacén y Gestión de Inventarios",
        "code": "EC0088",
        "trade": "logistics",
        "authority": "CONOCER",
        "level": "intermediate",
        "duration_hours": 100,
        "cost_mxn": 2500,
        "passing_score": 75,
        "us_equivalent": "APICS CPIM (Certified in Production and Inventory Management)",
        "description_es": "Gestión de almacenes: recepción, almacenamiento, surtido de pedidos, inventario cíclico y uso de WMS (Warehouse Management System).",
        "description_en": "Warehouse management: receiving, storage, order fulfillment, cycle inventory, and WMS usage.",
    },
    {
        "name": "Operaciones de Comercio Exterior y Aduanas",
        "code": "EC0312",
        "trade": "logistics",
        "authority": "CONOCER",
        "level": "advanced",
        "duration_hours": 150,
        "cost_mxn": 4000,
        "passing_score": 80,
        "us_equivalent": "NCBFAA Certified Customs Specialist",
        "description_es": "Clasificación arancelaria, pedimentos, IVA diferido, IMMEX/Maquiladora, operaciones USMCA/T-MEC y cumplimiento SAT para exportación.",
        "description_en": "Tariff classification, customs declarations, deferred VAT, IMMEX/Maquiladora, USMCA/T-MEC operations, and SAT export compliance.",
    },
    # ── Manufacturing / Manufactura ───────────────────────────────────────
    {
        "name": "Operador de Manufactura y Control de Calidad",
        "code": "EC0066",
        "trade": "manufacturing",
        "authority": "CONOCER",
        "level": "basic",
        "duration_hours": 80,
        "cost_mxn": 1600,
        "passing_score": 70,
        "us_equivalent": "ASQ Certified Quality Technician (CQT) — Entry",
        "description_es": "Certificación para operadores de línea de manufactura. Incluye 5S, control estadístico de proceso (SPC), lectura de planos y herramientas básicas.",
        "description_en": "Certification for manufacturing line operators. Includes 5S, statistical process control (SPC), blueprint reading, and basic tools.",
    },
    {
        "name": "Técnico en Manufactura Esbelta (Lean)",
        "code": "CONALEP-LEAN",
        "trade": "manufacturing",
        "authority": "CONALEP",
        "level": "intermediate",
        "duration_hours": 120,
        "cost_mxn": 3000,
        "passing_score": 75,
        "us_equivalent": "SME Lean Bronze Certification",
        "description_es": "Manufactura esbelta: VSM, Kaizen, Kanban, SMED, Poka-Yoke, Jidoka y OEE. Aplicable en industrias automotriz, aeroespacial y electrónica.",
        "description_en": "Lean manufacturing: VSM, Kaizen, Kanban, SMED, Poka-Yoke, Jidoka, and OEE. Applicable in automotive, aerospace, and electronics industries.",
    },
    {
        "name": "Auditor Interno ISO 9001:2015",
        "code": "ISO9001-AUD",
        "trade": "manufacturing",
        "authority": "NOM",
        "level": "advanced",
        "duration_hours": 160,
        "cost_mxn": 5000,
        "passing_score": 80,
        "us_equivalent": "ASQ Certified Quality Auditor (CQA)",
        "description_es": "Certificación para auditor interno de sistemas de gestión de calidad ISO 9001:2015. Incluye planeación, ejecución de auditorías y reporteo de hallazgos.",
        "description_en": "Certification for ISO 9001:2015 quality management system internal auditor. Includes planning, audit execution, and findings reporting.",
    },
]


async def seed_certifications() -> int:
    """Insert certifications if not already present. Returns count inserted."""
    await init_db()
    inserted = 0
    async with AsyncSessionLocal() as session:
        for cert_data in CERTIFICATIONS:
            existing = await session.execute(
                select(CertificationDB).where(CertificationDB.code == cert_data["code"])
            )
            if existing.scalar_one_or_none() is None:
                session.add(CertificationDB(**cert_data))
                inserted += 1
        await session.commit()
    return inserted


def run_seed() -> None:
    """Entry point for CLI seed command."""
    asyncio.run(_seed_and_print())


async def _seed_and_print() -> None:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    console = Console()
    console.print("[dim]Seeding certifications...[/dim]")
    count = await seed_certifications()
    if count == 0:
        console.print("[yellow]All certifications already seeded.[/yellow]")
        return
    table = Table("Code", "Name", "Trade", "Authority", "Level", "Cost MXN", box=box.ROUNDED)
    for c in CERTIFICATIONS:
        table.add_row(c["code"], c["name"][:45], c["trade"], c["authority"], c["level"], f"${c['cost_mxn']:,}")
    console.print(table)
    console.print(f"[green]✓ Seeded {count} certifications[/green]")
