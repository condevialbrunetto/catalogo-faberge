#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Análise Individual para Integração N8N
================================================

Script simples para análise de uma única peça Fabergé.
Recebe argumentos via linha de comando e retorna JSON para stdout.

Uso:
    python3 analyze_single.py "Nome da Peça" "Descrição das Marcas"

Exemplo:
    python3 analyze_single.py "Renaissance Egg" "Fabergé, M. P. in Cyrillic, 56, crossed anchors and scepter"

Author: Sistema de Análise Fabergé
Date: January 2026
"""

import sys
import json
from faberge_hallmark_analyzer import FabergeHallmarkAnalyzer


def main():
    """Função principal"""
    
    # Verificar argumentos
    if len(sys.argv) < 3:
        error_response = {
            "error": "Missing arguments",
            "usage": "python3 analyze_single.py <piece_name> <marks_text>",
            "example": 'python3 analyze_single.py "Renaissance Egg" "Fabergé, M.P., 56"'
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.exit(1)
    
    # Obter argumentos
    piece_name = sys.argv[1]
    marks = sys.argv[2]
    
    # Validar entrada
    if not piece_name or not marks:
        error_response = {
            "error": "Empty arguments",
            "piece_name": piece_name,
            "marks": marks
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.exit(1)
    
    try:
        # Criar analisador
        analyzer = FabergeHallmarkAnalyzer()
        
        # Analisar marcas
        result = analyzer.analyze_marks(marks, piece_name)
        
        # Converter para dicionário
        result_dict = result.to_dict()
        
        # Adicionar metadados
        result_dict["metadata"] = {
            "analyzer_version": "1.0",
            "method": "Zolonitsky",
            "analysis_type": "single_piece"
        }
        
        # Output JSON para stdout
        print(json.dumps(result_dict, ensure_ascii=False, indent=2))
        
        # Exit code baseado em confiança
        if result.confidence_score >= 0.5:
            sys.exit(0)  # Sucesso com alta confiança
        elif result.confidence_score > 0:
            sys.exit(0)  # Sucesso com confiança parcial
        else:
            sys.exit(2)  # Sucesso mas sem marcas identificadas
            
    except Exception as e:
        error_response = {
            "error": "Analysis failed",
            "exception": str(e),
            "piece_name": piece_name,
            "marks": marks
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
