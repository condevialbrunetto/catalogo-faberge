#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fabergé Hallmark Analysis System
=================================

Sistema de análise automatizada de punções (marcas de joalheiro) de peças Fabergé.
Identifica marcas de ensaiadores russos, marcas da Casa Fabergé, marcas imperiais,
e assinaturas de workmasters.

Author: Sistema de Análise Fabergé
Date: January 2026
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class MetalStandard(Enum):
    """Padrões de pureza de metal segundo o método Zolonitsky (sistema russo de zolotniki)"""
    SILVER_84 = ("84", 0.875, "875/1000 silver")  # 84 zolotniki
    SILVER_88 = ("88", 0.916, "916/1000 silver - Sterling equivalent")  # 88 zolotniki
    SILVER_91 = ("91", 0.947, "947/1000 silver - High grade")  # 91 zolotniki
    GOLD_56 = ("56", 0.583, "583/1000 gold - 14kt")  # 56 zolotniki
    GOLD_72 = ("72", 0.750, "750/1000 gold - 18kt")  # 72 zolotniki
    
    def __init__(self, mark: str, decimal: float, description: str):
        self.mark = mark
        self.decimal = decimal
        self.description = description


class AssayerPeriod(Enum):
    """Períodos de marcação de ensaiadores russos"""
    PRE_1899 = ("pre-1899", "Crossed anchors and scepter", "Âncoras cruzadas e cetro")
    POST_1899_PRE_1908 = ("1899-1908", "Kokoshnik preparation", "Período de transição")
    POST_1908 = ("post-1908", "Kokoshnik system", "Sistema kokoshnik (cabeça feminina)")


@dataclass
class AssayerMark:
    """Marca de ensaiador russo"""
    type: str  # "kokoshnik_left", "kokoshnik_right", "crossed_anchors", etc.
    period: str  # Pre-1899, 1899-1908, Post-1908
    direction: Optional[str] = None  # "left", "right" (para kokoshnik)
    assayer_monogram: Optional[str] = None  # e.g., "Y.L." (Yakov Lyapunov)
    description: str = ""
    
    def get_period_description(self) -> str:
        """Retorna descrição do período"""
        if self.period == "pre-1899":
            return "Pré-1899: Âncoras cruzadas e cetro"
        elif self.period == "post-1908":
            direction_text = f" voltada para {'esquerda' if self.direction == 'left' else 'direita'}" if self.direction else ""
            return f"Pós-1908: Kokoshnik (cabeça feminina{direction_text})"
        else:
            return "Período de transição (1899-1908)"


@dataclass
class ImperialMark:
    """Marca imperial russa"""
    type: str  # "double_headed_eagle", "imperial_warrant", etc.
    description: str
    period: str = "1885-1917"
    
    def __post_init__(self):
        if self.type == "double_headed_eagle":
            self.description = "Águia bicéfala imperial - Peça com autorização imperial"


@dataclass
class WorkmasterMark:
    """Marca de workmaster (mestre-de-obra)"""
    initials: str  # "M.P.", "H.W.", "A.H.", etc.
    name: str  # "Mikhail Perkhin", "Henrik Wigström", etc.
    period: str  # Período ativo
    workshop_location: str = "St. Petersburg"
    
    @staticmethod
    def get_known_workmasters() -> Dict[str, 'WorkmasterMark']:
        """Retorna dicionário de workmasters conhecidos"""
        return {
            "M.P.": WorkmasterMark("M.P.", "Mikhail Perkhin", "1886-1903", "St. Petersburg"),
            "М.П.": WorkmasterMark("М.П.", "Mikhail Perkhin (Cyrillic)", "1886-1903", "St. Petersburg"),
            "H.W.": WorkmasterMark("H.W.", "Henrik Wigström", "1903-1917", "St. Petersburg"),
            "A.H.": WorkmasterMark("A.H.", "August Holmström", "until 1903", "St. Petersburg"),
            "АН": WorkmasterMark("АН", "August Holmström (Cyrillic)", "until 1903", "St. Petersburg"),
            "E.K.": WorkmasterMark("E.K.", "Erik Kollin", "1870-1901", "St. Petersburg"),
            "EK": WorkmasterMark("EK", "Erik Kollin", "1870-1901", "St. Petersburg"),
            "I.P.": WorkmasterMark("I.P.", "Julius Alexander Rappoport", "1883-1908", "St. Petersburg"),
            "I.Р.": WorkmasterMark("I.Р.", "Julius Alexander Rappoport (Cyrillic)", "1883-1908", "St. Petersburg"),
            "A*H": WorkmasterMark("A*H", "August Hollming", "1880-1913", "St. Petersburg"),
            "O.P.": WorkmasterMark("O.P.", "Oscar Pihl Senior", "1887-1897", "Moscow"),
            "OP": WorkmasterMark("OP", "Oscar Pihl Senior", "1887-1897", "Moscow"),
        }


@dataclass
class FabergeMark:
    """Marca da Casa Fabergé"""
    variant: str  # "К.ФАБЕРЖЕ", "ФАБЕРЖЕ", "FABERGE", "K", etc.
    script: str  # "Cyrillic", "Latin", "Initial"
    period: str = "1882-1917"
    description: str = ""
    
    @staticmethod
    def get_known_variants() -> Dict[str, str]:
        """Retorna variantes conhecidas da marca Fabergé"""
        return {
            "К.ФАБЕРЖЕ": "Carl Fabergé - Nome completo em cirílico",
            "ФАБЕРЖЕ": "Fabergé - Sobrenome em cirílico (sem inicial)",
            "FABERGE": "Fabergé - Grafia latina",
            "K.FABERGE": "K. Fabergé - Inicial e sobrenome em latino",
            "K": "Marca reduzida - Apenas inicial K",
            "КФ": "Monograma КФ (Karl Fabergé)",
        }


@dataclass
class HallmarkAnalysisResult:
    """Resultado completo da análise de punções de uma peça"""
    piece_name: str
    metal_standard: Optional[MetalStandard] = None
    assayer_mark: Optional[AssayerMark] = None
    imperial_mark: Optional[ImperialMark] = None
    faberge_mark: Optional[FabergeMark] = None
    workmaster_mark: Optional[WorkmasterMark] = None
    additional_marks: List[str] = None
    repeated_marks: bool = False
    raw_marks_text: str = ""
    confidence_score: float = 0.0
    
    def __post_init__(self):
        if self.additional_marks is None:
            self.additional_marks = []
    
    def to_dict(self) -> Dict:
        """Converte resultado para dicionário (para JSON)"""
        result = {
            "piece_name": self.piece_name,
            "raw_marks_text": self.raw_marks_text,
            "confidence_score": self.confidence_score,
            "repeated_marks": self.repeated_marks,
        }
        
        if self.metal_standard:
            result["metal_standard"] = {
                "mark": self.metal_standard.mark,
                "purity": self.metal_standard.decimal,
                "description": self.metal_standard.description,
            }
        
        if self.assayer_mark:
            result["assayer_mark"] = asdict(self.assayer_mark)
        
        if self.imperial_mark:
            result["imperial_mark"] = asdict(self.imperial_mark)
        
        if self.faberge_mark:
            result["faberge_mark"] = asdict(self.faberge_mark)
        
        if self.workmaster_mark:
            result["workmaster_mark"] = asdict(self.workmaster_mark)
        
        if self.additional_marks:
            result["additional_marks"] = self.additional_marks
        
        return result


class FabergeHallmarkAnalyzer:
    """
    Analisador principal de punções Fabergé
    
    Implementa o método Zolonitsky para identificação de padrões de metal
    e análise completa de marcas presentes em peças Fabergé.
    """
    
    def __init__(self):
        self.known_workmasters = WorkmasterMark.get_known_workmasters()
        self.faberge_variants = FabergeMark.get_known_variants()
    
    def analyze_marks(self, marks_text: str, piece_name: str = "Unknown") -> HallmarkAnalysisResult:
        """
        Analisa texto de marcas e retorna resultado estruturado
        
        Args:
            marks_text: Texto descrevendo as marcas da peça
            piece_name: Nome da peça sendo analisada
            
        Returns:
            HallmarkAnalysisResult com todas as marcas identificadas
        """
        result = HallmarkAnalysisResult(
            piece_name=piece_name,
            raw_marks_text=marks_text
        )
        
        if not marks_text or marks_text.lower() in ["unknown", "unmarked", "n/a"]:
            result.confidence_score = 0.0
            return result
        
        # Identificar padrão de metal (Método Zolonitsky)
        result.metal_standard = self._identify_metal_standard(marks_text)
        
        # Identificar marca de ensaiador
        result.assayer_mark = self._identify_assayer_mark(marks_text)
        
        # Identificar marca imperial
        result.imperial_mark = self._identify_imperial_mark(marks_text)
        
        # Identificar marca Fabergé
        result.faberge_mark = self._identify_faberge_mark(marks_text)
        
        # Identificar workmaster
        result.workmaster_mark = self._identify_workmaster(marks_text)
        
        # Verificar marcas repetidas
        result.repeated_marks = self._check_repeated_marks(marks_text)
        
        # Calcular confiança
        result.confidence_score = self._calculate_confidence(result)
        
        return result
    
    def _identify_metal_standard(self, marks_text: str) -> Optional[MetalStandard]:
        """Identifica o padrão de metal usando o método Zolonitsky"""
        marks_lower = marks_text.lower()
        
        # Procurar por números de zolotniki
        for standard in MetalStandard:
            # Procurar pelo número exato
            pattern = rf'\b{standard.mark}\b'
            if re.search(pattern, marks_text):
                return standard
        
        return None
    
    def _identify_assayer_mark(self, marks_text: str) -> Optional[AssayerMark]:
        """Identifica marca de ensaiador russo"""
        marks_lower = marks_text.lower()
        
        # Verificar kokoshnik (pós-1908)
        if "kokoshnik" in marks_lower:
            direction = None
            if "right" in marks_lower or "direita" in marks_lower:
                direction = "right"
            elif "left" in marks_lower or "esquerda" in marks_lower:
                direction = "left"
            
            # Procurar monograma de ensaiador
            monogram = None
            if "y.l." in marks_lower or "y. l." in marks_lower:
                monogram = "Y.L. (Yakov Lyapunov)"
            elif "yakov lyapunov" in marks_lower:
                monogram = "Y.L. (Yakov Lyapunov)"
            
            return AssayerMark(
                type="kokoshnik",
                period="post-1908",
                direction=direction,
                assayer_monogram=monogram,
                description="Sistema kokoshnik - cabeça feminina com kokoshnik (chapéu tradicional russo)"
            )
        
        # Verificar âncoras cruzadas e cetro (pré-1899)
        if ("crossed anchors" in marks_lower or "âncoras cruzadas" in marks_lower) and \
           ("scepter" in marks_lower or "cetro" in marks_lower):
            return AssayerMark(
                type="crossed_anchors_scepter",
                period="pre-1899",
                description="Âncoras cruzadas e cetro - marca de São Petersburgo pré-1899"
            )
        
        return None
    
    def _identify_imperial_mark(self, marks_text: str) -> Optional[ImperialMark]:
        """Identifica marca imperial"""
        marks_lower = marks_text.lower()
        
        if "eagle" in marks_lower or "águia" in marks_lower or \
           "double-headed" in marks_lower or "bicéfala" in marks_lower or \
           "bicéfalo" in marks_lower:
            return ImperialMark(
                type="double_headed_eagle",
                description="Águia bicéfala imperial - Autorização da Corte Imperial"
            )
        
        if "imperial warrant" in marks_lower or "autorização imperial" in marks_lower:
            return ImperialMark(
                type="imperial_warrant",
                description="Autorização Imperial - Fornecedor da Corte Imperial"
            )
        
        return None
    
    def _identify_faberge_mark(self, marks_text: str) -> Optional[FabergeMark]:
        """Identifica marca da Casa Fabergé"""
        # Procurar variantes conhecidas
        for variant, description in self.faberge_variants.items():
            if variant in marks_text:
                script = "Cyrillic" if any(c in variant for c in "КФАБЕРЖЕ") else "Latin"
                if variant == "K":
                    script = "Initial"
                
                return FabergeMark(
                    variant=variant,
                    script=script,
                    description=description
                )
        
        # Procurar por padrões mais gerais
        if re.search(r'faberge|fabergé', marks_text, re.IGNORECASE):
            return FabergeMark(
                variant="FABERGE",
                script="Latin",
                description="Marca Fabergé (variante latina)"
            )
        
        return None
    
    def _identify_workmaster(self, marks_text: str) -> Optional[WorkmasterMark]:
        """Identifica marca de workmaster"""
        # Procurar por padrões especiais primeiro
        if "M. P. in Cyrillic" in marks_text or "M.P. in Cyrillic" in marks_text or "М.П." in marks_text:
            return self.known_workmasters["M.P."]
        
        if "H. W. in Cyrillic" in marks_text or "H.W. in Cyrillic" in marks_text:
            return self.known_workmasters["H.W."]
        
        if "A. H. in Cyrillic" in marks_text or "A.H. in Cyrillic" in marks_text:
            return self.known_workmasters["A.H."]
        
        # Procurar por iniciais conhecidas (com e sem pontos)
        for initials, workmaster in self.known_workmasters.items():
            # Criar padrão para encontrar as iniciais com ou sem pontos
            initials_no_dot = initials.replace(".", "")
            patterns = [
                rf'\b{re.escape(initials)}\b',
                rf'\b{re.escape(initials_no_dot)}\b',
            ]
            
            for pattern in patterns:
                if re.search(pattern, marks_text, re.IGNORECASE):
                    return workmaster
        
        # Procurar por nomes completos
        workmaster_names = {
            "perkhin": self.known_workmasters["M.P."],
            "perchin": self.known_workmasters["M.P."],
            "wigström": self.known_workmasters["H.W."],
            "wigstrom": self.known_workmasters["H.W."],
            "holmström": self.known_workmasters["A.H."],
            "holmstrom": self.known_workmasters["A.H."],
            "kollin": self.known_workmasters["E.K."],
            "rappoport": self.known_workmasters["I.P."],
        }
        
        marks_lower = marks_text.lower()
        for name, workmaster in workmaster_names.items():
            if name in marks_lower:
                return workmaster
        
        return None
    
    def _check_repeated_marks(self, marks_text: str) -> bool:
        """Verifica se há indicação de marcas repetidas"""
        marks_lower = marks_text.lower()
        repeated_indicators = [
            "repeated", "repetido", "repetida", "duplicate", "duplicado",
            "twice", "duas vezes", "multiple", "múltiplas"
        ]
        
        return any(indicator in marks_lower for indicator in repeated_indicators)
    
    def _calculate_confidence(self, result: HallmarkAnalysisResult) -> float:
        """
        Calcula score de confiança baseado nas marcas identificadas
        
        Score máximo: 1.0
        - Metal standard: 0.2
        - Assayer mark: 0.2
        - Fabergé mark: 0.3
        - Workmaster mark: 0.2
        - Imperial mark: 0.1
        """
        score = 0.0
        
        if result.metal_standard:
            score += 0.2
        
        if result.assayer_mark:
            score += 0.2
        
        if result.faberge_mark:
            score += 0.3
        
        if result.workmaster_mark:
            score += 0.2
        
        if result.imperial_mark:
            score += 0.1
        
        return round(score, 2)
    
    def analyze_collection(self, collection_data: List[Dict]) -> List[Dict]:
        """
        Analisa uma coleção completa de peças
        
        Args:
            collection_data: Lista de dicionários com dados das peças
                            Cada item deve ter 'nome' e 'marks' ou 'marcas'
        
        Returns:
            Lista de resultados de análise em formato dicionário
        """
        results = []
        
        for item in collection_data:
            piece_name = item.get("nome", item.get("name", "Unknown"))
            marks = item.get("marks", item.get("marcas", ""))
            
            analysis = self.analyze_marks(marks, piece_name)
            results.append(analysis.to_dict())
        
        return results
    
    def export_to_json(self, results: List[Dict], output_file: str):
        """Exporta resultados para arquivo JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def generate_summary_report(self, results: List[Dict]) -> Dict:
        """
        Gera relatório resumido da análise
        
        Returns:
            Dicionário com estatísticas da coleção
        """
        total_pieces = len(results)
        pieces_with_faberge_mark = sum(1 for r in results if r.get("faberge_mark"))
        pieces_with_workmaster = sum(1 for r in results if r.get("workmaster_mark"))
        pieces_with_imperial = sum(1 for r in results if r.get("imperial_mark"))
        pieces_with_assayer = sum(1 for r in results if r.get("assayer_mark"))
        
        # Contagem de workmasters
        workmasters_count = {}
        for r in results:
            if r.get("workmaster_mark"):
                wm_name = r["workmaster_mark"]["name"]
                workmasters_count[wm_name] = workmasters_count.get(wm_name, 0) + 1
        
        # Contagem de padrões de metal
        metal_standards_count = {}
        for r in results:
            if r.get("metal_standard"):
                metal = r["metal_standard"]["mark"]
                metal_standards_count[metal] = metal_standards_count.get(metal, 0) + 1
        
        avg_confidence = sum(r.get("confidence_score", 0) for r in results) / total_pieces if total_pieces > 0 else 0
        
        return {
            "total_pieces": total_pieces,
            "pieces_with_faberge_mark": pieces_with_faberge_mark,
            "pieces_with_workmaster": pieces_with_workmaster,
            "pieces_with_imperial_mark": pieces_with_imperial,
            "pieces_with_assayer_mark": pieces_with_assayer,
            "workmasters_distribution": workmasters_count,
            "metal_standards_distribution": metal_standards_count,
            "average_confidence_score": round(avg_confidence, 2)
        }


def main():
    """Função principal para demonstração"""
    print("=" * 80)
    print("Sistema de Análise de Punções Fabergé")
    print("Método Zolonitsky para Identificação de Marcas")
    print("=" * 80)
    print()
    
    # Criar analisador
    analyzer = FabergeHallmarkAnalyzer()
    
    # Exemplos de análise
    examples = [
        {
            "nome": "First Hen Egg (1885)",
            "marks": "Unmarked"
        },
        {
            "nome": "Third Imperial Egg (1887)",
            "marks": "AH"
        },
        {
            "nome": "Coronation Egg (1897)",
            "marks": "Fabergé, M. P. in Cyrillic, 56, crossed anchors and scepter"
        },
        {
            "nome": "Lilies of the Valley Egg (1898)",
            "marks": "Fabergé, M. P. in Cyrillic, 56, kokoshnik, Y. L., initials of Inspector Yakov Lyapunov of St. Petersburg Standard Board"
        },
        {
            "nome": "Trans-Siberian Railway Egg (1900)",
            "marks": "Fabergé, M. P. in Cyrillic, 88, kokoshnik"
        },
    ]
    
    print("Analisando exemplos de ovos imperiais...\n")
    
    results = []
    for example in examples:
        result = analyzer.analyze_marks(example["marks"], example["nome"])
        result_dict = result.to_dict()
        results.append(result_dict)
        
        print(f"Peça: {result.piece_name}")
        print(f"Marcas originais: {result.raw_marks_text}")
        print(f"Score de confiança: {result.confidence_score}")
        
        if result_dict.get('metal_standard'):
            ms = result_dict['metal_standard']
            print(f"  ✓ Padrão de metal: {ms['mark']} zolotniki ({ms['description']})")
        
        if result_dict.get('assayer_mark'):
            am = result_dict['assayer_mark']
            print(f"  ✓ Marca de ensaiador: {am['type']} ({am['period']})")
            if am.get('assayer_monogram'):
                print(f"    Monograma: {am['assayer_monogram']}")
        
        if result_dict.get('faberge_mark'):
            fm = result_dict['faberge_mark']
            print(f"  ✓ Marca Fabergé: {fm['variant']} ({fm['script']})")
        
        if result_dict.get('workmaster_mark'):
            wm = result_dict['workmaster_mark']
            print(f"  ✓ Workmaster: {wm['name']} ({wm['initials']})")
        
        if result_dict.get('imperial_mark'):
            im = result_dict['imperial_mark']
            print(f"  ✓ Marca Imperial: {im['description']}")
        
        print()
    
    # Gerar relatório resumido
    summary = analyzer.generate_summary_report(results)
    
    print("=" * 80)
    print("RELATÓRIO RESUMIDO")
    print("=" * 80)
    print(f"Total de peças analisadas: {summary['total_pieces']}")
    print(f"Peças com marca Fabergé: {summary['pieces_with_faberge_mark']}")
    print(f"Peças com workmaster identificado: {summary['pieces_with_workmaster']}")
    print(f"Peças com marca imperial: {summary['pieces_with_imperial_mark']}")
    print(f"Peças com marca de ensaiador: {summary['pieces_with_assayer_mark']}")
    print(f"Score médio de confiança: {summary['average_confidence_score']}")
    print()
    
    if summary['workmasters_distribution']:
        print("Distribuição de Workmasters:")
        for wm, count in summary['workmasters_distribution'].items():
            print(f"  - {wm}: {count} peça(s)")
    print()
    
    if summary['metal_standards_distribution']:
        print("Distribuição de Padrões de Metal:")
        for metal, count in summary['metal_standards_distribution'].items():
            print(f"  - {metal} zolotniki: {count} peça(s)")
    print()
    
    # Exportar para JSON
    output_file = "analise_puncoes_exemplo.json"
    analyzer.export_to_json(results, output_file)
    print(f"✓ Resultados exportados para: {output_file}")
    print()


if __name__ == "__main__":
    main()
