#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Processamento de Punções da Coleção Fabergé
======================================================

Processa o arquivo ovos_extraidos.json e analisa todas as marcas/punções
dos ovos imperiais Fabergé usando o sistema de análise de hallmarks.

Author: Sistema de Análise Fabergé
Date: January 2026
"""

import json
import sys
from pathlib import Path
from faberge_hallmark_analyzer import FabergeHallmarkAnalyzer


# Mapeamento de padrões de metal Zolonitsky para tipo de metal
METAL_TYPE_MAP = {
    "56": "ouro",
    "72": "ouro",
    "84": "prata",
    "88": "prata",
    "91": "prata"
}


def load_collection_data(input_file: str) -> list:
    """Carrega dados da coleção do arquivo JSON"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Carregados {len(data)} ovos imperiais de: {input_file}")
        return data
    except FileNotFoundError:
        print(f"✗ Arquivo não encontrado: {input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Erro ao decodificar JSON: {e}")
        sys.exit(1)


def process_collection(collection_data: list, analyzer: FabergeHallmarkAnalyzer) -> list:
    """
    Processa toda a coleção e retorna resultados
    
    Args:
        collection_data: Lista com dados dos ovos
        analyzer: Instância do analisador de hallmarks
    
    Returns:
        Lista de resultados da análise
    """
    results = []
    
    print("\nProcessando coleção...")
    print("=" * 80)
    
    for idx, ovo in enumerate(collection_data, 1):
        nome = ovo.get("nome", "Unknown")
        ano = ovo.get("ano", "Unknown")
        workmaster = ovo.get("workmaster", "N/A")
        marks = ovo.get("marks", "Unknown")
        
        # Criar identificador completo
        piece_name = f"{nome} ({ano})"
        
        # Analisar marcas
        result = analyzer.analyze_marks(marks, piece_name)
        result_dict = result.to_dict()
        
        # Adicionar informações adicionais do JSON original
        result_dict["year"] = ano
        result_dict["materials"] = ovo.get("materials", "N/A")
        result_dict["dimensions"] = ovo.get("dimensions", "N/A")
        
        # Obter proveniência uma única vez
        provenance = ovo.get("provenance", "N/A")
        result_dict["provenance_summary"] = provenance[:200] + "..." if len(provenance) > 200 else provenance
        
        results.append(result_dict)
        
        # Mostrar progresso
        confidence_indicator = "✓" if result.confidence_score >= 0.5 else "◐" if result.confidence_score > 0 else "✗"
        print(f"{confidence_indicator} [{idx:02d}/{len(collection_data)}] {nome} ({ano}) - Confiança: {result.confidence_score}")
    
    print("=" * 80)
    print(f"✓ Processamento concluído: {len(results)} peças analisadas\n")
    
    return results


def generate_detailed_report(results: list, analyzer: FabergeHallmarkAnalyzer):
    """Gera relatório detalhado da análise"""
    
    summary = analyzer.generate_summary_report(results)
    
    print("=" * 80)
    print("RELATÓRIO DETALHADO DA ANÁLISE DE PUNÇÕES")
    print("=" * 80)
    print()
    
    # Estatísticas gerais
    print("📊 ESTATÍSTICAS GERAIS")
    print("-" * 80)
    print(f"Total de ovos imperiais analisados: {summary['total_pieces']}")
    print(f"Ovos com marca Fabergé identificada: {summary['pieces_with_faberge_mark']} ({summary['pieces_with_faberge_mark']/summary['total_pieces']*100:.1f}%)")
    print(f"Ovos com workmaster identificado: {summary['pieces_with_workmaster']} ({summary['pieces_with_workmaster']/summary['total_pieces']*100:.1f}%)")
    print(f"Ovos com marca imperial: {summary['pieces_with_imperial_mark']} ({summary['pieces_with_imperial_mark']/summary['total_pieces']*100:.1f}%)")
    print(f"Ovos com marca de ensaiador: {summary['pieces_with_assayer_mark']} ({summary['pieces_with_assayer_mark']/summary['total_pieces']*100:.1f}%)")
    print(f"Score médio de confiança: {summary['average_confidence_score']:.2f}")
    print()
    
    # Distribuição de workmasters
    if summary['workmasters_distribution']:
        print("🔨 DISTRIBUIÇÃO DE WORKMASTERS (Mestres-de-Obra)")
        print("-" * 80)
        sorted_wm = sorted(summary['workmasters_distribution'].items(), key=lambda x: x[1], reverse=True)
        for wm, count in sorted_wm:
            percentage = count / summary['total_pieces'] * 100
            bar = "█" * int(percentage / 2)
            print(f"{wm:40s} {count:3d} ovos {bar} {percentage:5.1f}%")
        print()
    
    # Distribuição de padrões de metal
    if summary['metal_standards_distribution']:
        print("🥇 DISTRIBUIÇÃO DE PADRÕES DE METAL (Método Zolonitsky)")
        print("-" * 80)
        
        sorted_metals = sorted(summary['metal_standards_distribution'].items(), key=lambda x: x[1], reverse=True)
        for metal, count in sorted_metals:
            percentage = count / summary['total_pieces'] * 100
            bar = "█" * int(percentage / 2)
            # Determinar tipo de metal usando mapeamento global
            metal_type = METAL_TYPE_MAP.get(metal, "desconhecido")
            print(f"{metal} zolotniki ({metal_type:5s}) {count:3d} ovos {bar} {percentage:5.1f}%")
        print()
    
    # Análise de períodos de ensaiadores
    print("📅 ANÁLISE DE PERÍODOS DE MARCAÇÃO")
    print("-" * 80)
    pre_1899 = sum(1 for r in results if r.get("assayer_mark") and r["assayer_mark"]["period"] == "pre-1899")
    post_1908 = sum(1 for r in results if r.get("assayer_mark") and r["assayer_mark"]["period"] == "post-1908")
    
    if pre_1899 > 0:
        print(f"Pré-1899 (âncoras cruzadas e cetro): {pre_1899} ovos")
    if post_1908 > 0:
        print(f"Pós-1908 (sistema kokoshnik): {post_1908} ovos")
    
    unknown_period = summary['total_pieces'] - pre_1899 - post_1908
    if unknown_period > 0:
        print(f"Período não identificado ou sem marcas: {unknown_period} ovos")
    print()
    
    # Top 10 ovos com maior confiança
    print("🏆 TOP 10 OVOS COM MARCAÇÃO MAIS COMPLETA")
    print("-" * 80)
    sorted_by_confidence = sorted(results, key=lambda x: x.get("confidence_score", 0), reverse=True)[:10]
    for idx, result in enumerate(sorted_by_confidence, 1):
        score = result.get("confidence_score", 0)
        name = result.get("piece_name", "Unknown")
        print(f"{idx:2d}. {name:50s} Score: {score:.2f}")
    print()
    
    # Ovos sem marcas ou com baixa identificação
    low_confidence = [r for r in results if r.get("confidence_score", 0) < 0.3]
    if low_confidence:
        print("⚠️  OVOS COM MARCAÇÃO INCOMPLETA OU AUSENTE")
        print("-" * 80)
        print(f"Total: {len(low_confidence)} ovos com score < 0.3")
        for result in low_confidence[:5]:  # Mostrar primeiros 5
            name = result.get("piece_name", "Unknown")
            score = result.get("confidence_score", 0)
            marks = result.get("raw_marks_text", "")
            print(f"  • {name}")
            print(f"    Marcas: {marks}")
            print(f"    Score: {score:.2f}")
        if len(low_confidence) > 5:
            print(f"  ... e mais {len(low_confidence) - 5} ovos")
        print()


def export_results(results: list, output_dir: str = "."):
    """Exporta resultados em múltiplos formatos"""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # JSON completo
    json_file = output_path / "analise_puncoes_colecao_completa.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✓ JSON completo exportado: {json_file}")
    
    # JSON resumido (apenas informações essenciais)
    resumido = []
    for r in results:
        resumido.append({
            "piece": r["piece_name"],
            "year": r.get("year"),
            "confidence": r["confidence_score"],
            "faberge_mark": r.get("faberge_mark", {}).get("variant") if r.get("faberge_mark") else None,
            "workmaster": r.get("workmaster_mark", {}).get("name") if r.get("workmaster_mark") else None,
            "metal": r.get("metal_standard", {}).get("mark") if r.get("metal_standard") else None,
            "assayer_period": r.get("assayer_mark", {}).get("period") if r.get("assayer_mark") else None,
        })
    
    json_resumido = output_path / "analise_puncoes_resumo.json"
    with open(json_resumido, 'w', encoding='utf-8') as f:
        json.dump(resumido, f, ensure_ascii=False, indent=2)
    print(f"✓ JSON resumido exportado: {json_resumido}")
    
    # Markdown report
    md_file = output_path / "RELATORIO_ANALISE_PUNCOES.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Relatório de Análise de Punções Fabergé\n\n")
        f.write("Análise sistemática das marcas de joalheiro dos Ovos Imperiais Fabergé\n\n")
        f.write("---\n\n")
        f.write("## Resumo Executivo\n\n")
        f.write(f"- **Total de peças analisadas**: {len(results)}\n")
        
        avg_confidence = sum(r.get("confidence_score", 0) for r in results) / len(results)
        f.write(f"- **Score médio de confiança**: {avg_confidence:.2f}\n")
        
        with_marks = sum(1 for r in results if r.get("confidence_score", 0) > 0.3)
        f.write(f"- **Peças com marcação identificável**: {with_marks}\n\n")
        
        f.write("## Método de Análise\n\n")
        f.write("Este relatório utiliza o **Método Zolonitsky** para identificação de padrões de metal ")
        f.write("e análise sistemática de punções russas, incluindo:\n\n")
        f.write("1. **Marcas de ensaiadores russos** (84, 56, 72, 88, 91 zolotniki)\n")
        f.write("2. **Sistema kokoshnik** (pós-1908) vs. **âncoras cruzadas** (pré-1899)\n")
        f.write("3. **Marcas da Casa Fabergé** (К.ФАБЕРЖЕ, ФАБЕРЖЕ, etc.)\n")
        f.write("4. **Marcas imperiais** (águia bicéfala)\n")
        f.write("5. **Assinaturas de workmasters** (M.P., H.W., A.H., etc.)\n\n")
        
        f.write("---\n\n")
        f.write("## Detalhamento por Peça\n\n")
        
        for result in results:
            f.write(f"### {result['piece_name']}\n\n")
            f.write(f"**Score de Confiança**: {result['confidence_score']:.2f}\n\n")
            
            if result.get("metal_standard"):
                ms = result["metal_standard"]
                f.write(f"- **Padrão de Metal**: {ms['mark']} zolotniki ({ms['description']})\n")
            
            if result.get("faberge_mark"):
                fm = result["faberge_mark"]
                f.write(f"- **Marca Fabergé**: {fm['variant']} ({fm['script']})\n")
            
            if result.get("workmaster_mark"):
                wm = result["workmaster_mark"]
                f.write(f"- **Workmaster**: {wm['name']} ({wm['initials']}) - Ativo: {wm['period']}\n")
            
            if result.get("assayer_mark"):
                am = result["assayer_mark"]
                f.write(f"- **Marca de Ensaiador**: {am['type']} ({am['period']})\n")
                if am.get('assayer_monogram'):
                    f.write(f"  - Monograma: {am['assayer_monogram']}\n")
            
            if result.get("imperial_mark"):
                im = result["imperial_mark"]
                f.write(f"- **Marca Imperial**: {im['description']}\n")
            
            f.write(f"\n**Marcas originais**: `{result['raw_marks_text']}`\n\n")
            f.write("---\n\n")
    
    print(f"✓ Relatório Markdown exportado: {md_file}")
    print()


def main():
    """Função principal"""
    print("=" * 80)
    print("PROCESSAMENTO DE PUNÇÕES DA COLEÇÃO FABERGÉ")
    print("Sistema de Análise usando Método Zolonitsky")
    print("=" * 80)
    print()
    
    # Caminho do arquivo de entrada
    input_file = "ovos_extraidos.json"
    
    # Carregar dados
    collection_data = load_collection_data(input_file)
    
    # Criar analisador
    analyzer = FabergeHallmarkAnalyzer()
    
    # Processar coleção
    results = process_collection(collection_data, analyzer)
    
    # Gerar relatório detalhado
    generate_detailed_report(results, analyzer)
    
    # Exportar resultados
    export_results(results)
    
    print("=" * 80)
    print("✓ PROCESSAMENTO CONCLUÍDO COM SUCESSO")
    print("=" * 80)
    print()
    print("Arquivos gerados:")
    print("  • analise_puncoes_colecao_completa.json - Dados completos em JSON")
    print("  • analise_puncoes_resumo.json - Resumo em JSON")
    print("  • RELATORIO_ANALISE_PUNCOES.md - Relatório em Markdown")
    print()
    print("Integração N8N:")
    print("  Os arquivos JSON podem ser facilmente integrados em workflows N8N")
    print("  para automação e processamento adicional.")
    print()


if __name__ == "__main__":
    main()
