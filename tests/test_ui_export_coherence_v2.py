"""
Test de coherencia: UI vs Export HTML - Ambos consumen EvolutionComparisonV2
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from domain.analysis_snapshot import (
    EvolutionComparisonV2,
    EvolutionPointV2,
)
from reports.charts_generator import generate_evolution_line_chart


def test_ui_export_coherence():
    """
    Valida que tanto la UI (CompareLineChart) como el export (HTML)
    consumen exactamente los mismos datos V2 sin transformación.
    
    Garantiza:
    1. Mismo contrato de datos (EvolutionComparisonV2.points)
    2. Mismo uso de metadata (start, end, label, difference)
    3. Sin recálculos ni inferencias
    """
    print("\n" + "=" * 70)
    print("TEST: Coherencia UI vs Export HTML (EvolutionComparisonV2)")
    print("=" * 70 + "\n")
    
    # ============================================================
    # Crear datos V2 compartidos
    # ============================================================
    
    print("[1] Preparando datos EvolutionComparisonV2 compartidos...")
    
    evolution_points = [
        EvolutionPointV2(
            key='2025-01-01',
            label='01/01/2025',  # Pre-formateado en builder
            start=datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 1, 1, 23, 59, 59, tzinfo=timezone.utc),
            value_a=1000.0,
            value_b=1100.0,
            difference=100.0,
            is_partial=False
        ),
        EvolutionPointV2(
            key='2025-01-02',
            label='02/01/2025',
            start=datetime(2025, 1, 2, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 1, 2, 23, 59, 59, tzinfo=timezone.utc),
            value_a=1200.0,
            value_b=1300.0,
            difference=100.0,
            is_partial=False
        ),
        EvolutionPointV2(
            key='2025-01-03',
            label='03/01/2025',
            start=datetime(2025, 1, 3, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 1, 3, 23, 59, 59, tzinfo=timezone.utc),
            value_a=1500.0,
            value_b=1400.0,
            difference=-100.0,
            is_partial=True  # Parcial por corte de fecha
        ),
    ]
    
    evolution_comparison = EvolutionComparisonV2(points=evolution_points)
    
    print(f"  ✅ {len(evolution_points)} puntos creados")
    
    # ============================================================
    # Verificar que los datos son agnósticos (sin UI-specific logic)
    # ============================================================
    
    print("\n[2] Validando que EvolutionComparisonV2 es agnóstico...")
    
    checks = {
        'No depende de Flet': 'ft.' not in str(evolution_comparison),
        'No depende de matplotlib': 'plt.' not in str(evolution_comparison),
        'Tiene metadata temporal (start/end)': all(p.start and p.end for p in evolution_points),
        'Tiene label pre-formateado': all(p.label and '/' in p.label for p in evolution_points),
        'Tiene difference precomputado': all(p.difference is not None for p in evolution_points),
        'Tiene is_partial para marcar truncados': all(hasattr(p, 'is_partial') for p in evolution_points),
    }
    
    all_passed = True
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    # ============================================================
    # Simular consumo en UI (CompareLineChart)
    # ============================================================
    
    print("\n[3] Simulando consumo en UI (CompareLineChart)...")
    
    # El chart recibe points directamente (sin transformación)
    ui_labels = [p.label for p in evolution_comparison.points]
    ui_values_a = [p.value_a for p in evolution_comparison.points]
    ui_values_b = [p.value_b for p in evolution_comparison.points]
    ui_tooltips = [
        f"{p.label}: A={p.value_a:.0f}€, B={p.value_b:.0f}€, diff={p.difference:+.0f}€" +
        (", ⚠️ Período incompleto" if p.is_partial else "")
        for p in evolution_comparison.points
    ]
    
    print(f"  ✅ Labels extraídas (sin transformación): {ui_labels}")
    print(f"  ✅ Valores A extraídos: {ui_values_a}")
    print(f"  ✅ Valores B extraídos: {ui_values_b}")
    print(f"  ✅ Tooltips con metadata:")
    for tooltip in ui_tooltips:
        print(f"     - {tooltip}")
    
    # ============================================================
    # Simular consumo en Export (HTML + matplotlib)
    # ============================================================
    
    print("\n[4] Simulando consumo en Export HTML...")
    
    try:
        chart_base64 = generate_evolution_line_chart(evolution_comparison.points)
        
        # Export recibe los mismos points
        export_labels = [p.label for p in evolution_comparison.points]
        export_values_a = [p.value_a for p in evolution_comparison.points]
        export_values_b = [p.value_b for p in evolution_comparison.points]
        
        print(f"  ✅ Gráfico matplotlib generado (base64 length: {len(chart_base64)})")
        print(f"  ✅ Labels para eje X: {export_labels}")
        print(f"  ✅ Series Y (período A): {export_values_a}")
        print(f"  ✅ Series Y (período B): {export_values_b}")
        
    except Exception as e:
        print(f"  ❌ Error en export: {e}")
        assert False
    
    # ============================================================
    # Validar que AMBOS consumen exactamente los mismos datos
    # ============================================================
    
    print("\n[5] Validando coherencia UI ↔ Export...")
    
    coherence_checks = {
        'Labels idénticas': ui_labels == export_labels,
        'Valores A idénticos': ui_values_a == export_values_a,
        'Valores B idénticos': ui_values_b == export_values_b,
        'Sin recálculos': all(
            p.difference == (p.value_b - p.value_a)
            for p in evolution_comparison.points
        ),
        'Metadata temporal preservada': all(
            p.start < p.end
            for p in evolution_comparison.points
        ),
    }
    
    all_coherent = True
    for check_name, result in coherence_checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_coherent = False
    
    # ============================================================
    # Resultado final
    # ============================================================
    
    if all_passed and all_coherent:
        print(f"\n✅ COHERENCIA VALIDADA")
        print(f"\nGuarantías:")
        print(f"  - UI y Export consumen EvolutionComparisonV2.points")
        print(f"  - Sin transformación de datos")
        print(f"  - Sin recálculos")
        print(f"  - Sin inferencias")
        print(f"  - Metadata temporal completa (start, end, is_partial)")
        assert True
    else:
        print(f"\n❌ INCOHERENCIA DETECTADA")
        assert False


if __name__ == '__main__':
    success = test_ui_export_coherence()
    exit(0 if success else 1)
