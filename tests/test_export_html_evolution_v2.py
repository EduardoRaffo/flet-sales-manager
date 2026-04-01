"""
Test de integración: Export HTML con EvolutionComparisonV2
"""

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dataclasses import asdict

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from domain.analysis_snapshot import (
    AnalysisSnapshot,
    EvolutionComparisonV2,
    EvolutionPointV2,
    ComparisonSnapshot,
    ComparisonMetrics,
    ProductComparison,
    PeriodSnapshot,
    Metadata,
    Filters,
    TimeGrouping,
    AnalysisMode,
    PeriodMetrics,
    ClientRank,
    TableRow,
    ProductDistribution,
    EvolutionData
)
from reports.report_html import generate_html_report_from_snapshot


def test_export_evolution_comparison_v2():
    """
    Test que valida que export HTML consume EvolutionComparisonV2 correctamente.
    
    Verifica:
    1. Generación de puntos V2 con metadata temporal
    2. Creación de snapshot compare válido
    3. Exportación a HTML sin errores
    4. Presencia de gráfico de evolución en HTML
    """
    print("\n" + "=" * 70)
    print("TEST: Export HTML con EvolutionComparisonV2")
    print("=" * 70 + "\n")
    
    # ============================================================
    # Paso 1: Crear puntos de evolución V2
    # ============================================================
    
    print("[1] Creando puntos de evolución V2...")
    
    evolution_points = [
        EvolutionPointV2(
            key='2025-01-01',
            label='01/01',
            start=datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 1, 1, 23, 59, 59, tzinfo=timezone.utc),
            value_a=1000.0,
            value_b=1100.0,
            difference=100.0,
            is_partial=False
        ),
        EvolutionPointV2(
            key='2025-01-02',
            label='02/01',
            start=datetime(2025, 1, 2, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 1, 2, 23, 59, 59, tzinfo=timezone.utc),
            value_a=1500.0,
            value_b=1600.0,
            difference=100.0,
            is_partial=False
        ),
        EvolutionPointV2(
            key='2025-01-03',
            label='03/01',
            start=datetime(2025, 1, 3, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 1, 3, 23, 59, 59, tzinfo=timezone.utc),
            value_a=2000.0,
            value_b=1900.0,
            difference=-100.0,
            is_partial=True  # Período incompleto
        ),
        EvolutionPointV2(
            key='2025-01-04',
            label='04/01',
            start=datetime(2025, 1, 4, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 1, 4, 23, 59, 59, tzinfo=timezone.utc),
            value_a=1800.0,
            value_b=1950.0,
            difference=150.0,
            is_partial=False
        ),
    ]
    
    print(f"  ✅ {len(evolution_points)} puntos creados")
    for point in evolution_points:
        print(f"     - {point.label}: A={point.value_a:.0f}, B={point.value_b:.0f}, diff={point.difference:+.0f}")
    
    # ============================================================
    # Paso 2: Crear EvolutionComparisonV2
    # ============================================================
    
    print("\n[2] Creando EvolutionComparisonV2...")
    
    evolution_comparison = EvolutionComparisonV2(points=evolution_points)
    
    print(f"  ✅ EvolutionComparisonV2 creada con {len(evolution_comparison.points)} puntos")
    
    # ============================================================
    # Paso 3: Crear snapshot completo
    # ============================================================
    
    print("\n[3] Creando snapshot COMPARE completo...")
    
    # Metadata
    metadata = Metadata(
        mode=AnalysisMode.COMPARE,
        grouping=TimeGrouping.DAY,
        generated_at=datetime.now(timezone.utc)
    )
    
    # Filtros
    filters = Filters(
        date_start='2025-01-01',
        date_end='2025-01-04',
        client_name=None,
        product_type=None
    )
    
    # Métricas período A
    metrics_a = PeriodMetrics(
        total_sales=6300.0,
        transactions=25,
        avg_ticket=252.0,
        total_quantity=25,
        unique_clients=8
    )
    
    # Periodo A
    period_a = PeriodSnapshot(
        label='Período Principal',
        filters=filters,
        table_data=[
            TableRow('Producto A', 10, 3000.0, 300.0, 250.0, 350.0),
            TableRow('Producto B', 15, 3300.0, 220.0, 200.0, 250.0),
        ],
        metrics=metrics_a,
        evolution=EvolutionData(
            labels=[p.label for p in evolution_points],
            values=[p.value_a for p in evolution_points],
            grouping=TimeGrouping.DAY
        ),
        top_clients=[
            ClientRank(1, 'ACME Corp', 1500.0, 5, 23.8),
            ClientRank(2, 'TechCorp', 1200.0, 4, 19.0),
        ],
        product_distribution=ProductDistribution(
            labels=['Producto A', 'Producto B'],
            values=[3000.0, 3300.0],
            percentages=[47.6, 52.4]
        )
    )
    
    # Métricas período B
    metrics_b = PeriodMetrics(
        total_sales=6550.0,
        transactions=26,
        avg_ticket=251.9,
        total_quantity=26,
        unique_clients=9
    )
    
    filters_b = Filters(
        date_start='2025-01-01',
        date_end='2025-01-04',
        client_name=None,
        product_type=None
    )
    
    # Periodo B
    period_b = PeriodSnapshot(
        label='Período de Comparación',
        filters=filters_b,
        table_data=[
            TableRow('Producto A', 10, 3100.0, 310.0, 260.0, 360.0),
            TableRow('Producto B', 16, 3450.0, 215.6, 210.0, 260.0),
        ],
        metrics=metrics_b,
        evolution=EvolutionData(
            labels=[p.label for p in evolution_points],
            values=[p.value_b for p in evolution_points],
            grouping=TimeGrouping.DAY
        ),
        top_clients=[
            ClientRank(1, 'ACME Corp', 1600.0, 5, 24.4),
            ClientRank(2, 'TechCorp', 1300.0, 5, 19.8),
        ],
        product_distribution=ProductDistribution(
            labels=['Producto A', 'Producto B'],
            values=[3100.0, 3450.0],
            percentages=[47.3, 52.7]
        )
    )
    
    # Comparación
    comparison = ComparisonSnapshot(
        metrics=ComparisonMetrics(
            absolute_changes={
                'total_sales': 250.0,
                'transactions': 1,
                'avg_ticket': -0.1,
                'unique_clients': 1
            },
            percentage_changes={
                'total_sales': 3.97,
                'transactions': 4.0,
                'avg_ticket': -0.04,
                'unique_clients': 12.5
            }
        ),
        evolution=evolution_comparison,
        products=ProductComparison(
            labels=['Producto A', 'Producto B'],
            series_a=[3000.0, 3300.0],
            series_b=[3100.0, 3450.0],
            differences=[100.0, 150.0],
            percentage_diff=[3.33, 4.55]
        )
    )
    
    # Snapshot raíz
    snapshot = AnalysisSnapshot(
        metadata=metadata,
        filters=filters,
        period_a=period_a,
        period_b=period_b,
        comparison=comparison
    )
    
    print(f"  ✅ Snapshot COMPARE creado")
    print(f"     - Modo: {snapshot.metadata.mode}")
    print(f"     - Es COMPARE: {snapshot.is_compare_mode()}")
    print(f"     - Validación: {snapshot.validate()}")
    
    # ============================================================
    # Paso 4: Validar snapshot
    # ============================================================
    
    print("\n[4] Validando snapshot...")
    
    try:
        is_valid = snapshot.validate()
        print(f"  ✅ Snapshot válido: {is_valid}")
    except ValueError as e:
        print(f"  ❌ Validación fallida: {e}")
        assert False
    
    # ============================================================
    # Paso 5: Generar export HTML
    # ============================================================
    
    print("\n[5] Generando export HTML...")
    
    output_file = Path(__file__).parent.parent / "test_export_evolution_v2.html"
    
    try:
        success, message, filepath = generate_html_report_from_snapshot(
            snapshot,
            filename=str(output_file)
        )
        
        if success:
            print(f"  ✅ {message}")
            print(f"     Archivo: {filepath}")
        else:
            print(f"  ❌ {message}")
            return False
    except Exception as e:
        print(f"  ❌ Error generando export: {e}")
        import traceback
        traceback.print_exc()
        assert False
    
    # ============================================================
    # Paso 6: Validar contenido HTML
    # ============================================================
    
    print("\n[6] Validando contenido HTML...")
    
    if filepath and Path(filepath).exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar presencia de elementos clave
        checks = {
            'Comparación': 'Comparación' in content,
            'Evolución de Ventas Comparada': 'Evolución de Ventas Comparada' in content,
            'Cambios Absolutos': 'Cambios Absolutos' in content,
            'Cambios Porcentuales': 'Cambios Porcentuales' in content,
            'Gráfico de evolución (base64)': 'data:image/png;base64,' in content,
        }
        
        all_checks_passed = True
        for check_name, check_result in checks.items():
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}")
            if not check_result:
                all_checks_passed = False
        
        if all_checks_passed:
            print(f"\n✅ INTEGRACIÓN EXITOSA")
            print(f"\nResumen:")
            print(f"  - Puntos V2: {len(evolution_points)}")
            print(f"  - Snapshot válido: ✅")
            print(f"  - Export HTML: ✅")
            print(f"  - Gráfico de evolución: ✅")
            assert True
        else:
            print(f"\n❌ INTEGRACIÓN PARCIAL (faltan elementos)")
            assert False
    else:
        print(f"  ❌ Archivo no creado")
        assert False


if __name__ == '__main__':
    success = test_export_evolution_comparison_v2()
    exit(0 if success else 1)
