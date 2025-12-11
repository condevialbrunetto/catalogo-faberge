import re
import json

# Ler o arquivo completo
with open('/home/ubuntu/page_texts/fabergeresearch.com_eggs-faberge-imperial-egg-chronology_.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Lista de todos os ovos conforme o índice
ovos_lista = [
    ("First Hen Egg", "1885"),
    ("Hen Egg with Sapphire Pendant", "1886"),
    ("Third Imperial Egg", "1887"),
    ("Cherub Egg with Chariot", "1888"),
    ("Nécessaire Egg", "1889"),
    ("Danish Palaces Egg", "1890"),
    ("Memory of Azov Egg", "1891"),
    ("Diamond Trellis Egg", "1892"),
    ("Caucasus Egg", "1893"),
    ("Renaissance Egg", "1894"),
    ("Blue Serpent Clock Egg", "1895"),
    ("Rosebud Egg", "1895"),
    ("Alexander III Portraits Egg", "1896"),
    ("Egg with Revolving Miniatures", "1896"),
    ("Coronation Egg", "1897"),
    ("Mauve Egg with 3 Miniatures", "1897"),
    ("Lilies of the Valley Egg", "1898"),
    ("Pelican Egg", "1898"),
    ("Madonna Lily Clock Egg", "1899"),
    ("Pansy Egg", "1899"),
    ("Cockerel Egg", "1900"),
    ("Trans-Siberian Railway Egg", "1900"),
    ("Flower Basket Egg", "1901"),
    ("Gatchina Palace Egg", "1901"),
    ("Clover Leaf Egg", "1902"),
    ("Empire Nephrite Egg", "1902"),
    ("Peter the Great Egg", "1903"),
    ("Royal Danish Egg", "1903"),
    ("Alexander Palace Egg", "1908"),
    ("Peacock Egg", "1908"),
    ("Alexander III Commemorative Egg", "1909"),
    ("Standart Egg", "1909"),
    ("Alexander III Equestrian Egg", "1910"),
    ("Colonnade Egg", "1910"),
    ("15th Anniversary Egg", "1911"),
    ("Orange Tree Egg", "1911"),
    ("Napoleonic Egg", "1912"),
    ("Tsesarevich Egg", "1912"),
    ("Romanov Tercentenary Egg", "1913"),
    ("Winter Egg", "1913"),
    ("Catherine the Great Egg", "1914"),
    ("Mosaic Egg", "1914"),
    ("Red Cross Portraits Egg", "1915"),
    ("Red Cross Triptych Egg", "1915"),
    ("Order of St. George Egg", "1916"),
    ("Steel Military Egg", "1916"),
    ("Blue Tsesarevich Constellation Egg", "1917"),
    ("Karelian Birch Egg", "1917"),
    ("Moscow Kremlin Egg", "1906"),
    ("Love Trophies Egg", "1907"),
    ("Rose Trellis Egg", "1907"),
    ("Swan Egg", "1906")
]

# Extrair seções de cada ovo
ovos_data = []

for nome_ovo, ano in ovos_lista:
    # Procurar pela seção do ovo
    pattern = rf'{re.escape(nome_ovo)} \({ano}\)(.*?)(?=\n[A-Z][a-z]+ [A-Z][a-z]+ (?:Egg|with) \(\d{{4}}\)|\Z)'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if match:
        secao = match.group(0)
        
        # Extrair informações estruturadas
        workmaster = re.search(r'Workmaster:\s*(.+?)(?:\n|$)', secao)
        marks = re.search(r'Marks:\s*(.+?)(?:\n|$)', secao)
        materials = re.search(r'Materials:\s*(.+?)(?:\n|Dimensions)', secao, re.DOTALL)
        dimensions = re.search(r'Dimensions:\s*(.+?)(?:\n|Description)', secao, re.DOTALL)
        description = re.search(r'Description:\s*(.+?)(?:\n(?:Background Notes|Provenance))', secao, re.DOTALL)
        background = re.search(r'Background Notes:\s*(.+?)(?:\nProvenance)', secao, re.DOTALL)
        provenance = re.search(r'Provenance:\s*(.+?)$', secao, re.DOTALL)
        
        ovo_info = {
            'nome': nome_ovo,
            'ano': ano,
            'workmaster': workmaster.group(1).strip() if workmaster else 'N/A',
            'marks': marks.group(1).strip() if marks else 'N/A',
            'materials': materials.group(1).strip() if materials else 'N/A',
            'dimensions': dimensions.group(1).strip() if dimensions else 'N/A',
            'description': description.group(1).strip()[:500] if description else 'N/A',
            'background': background.group(1).strip()[:500] if background else 'N/A',
            'provenance': provenance.group(1).strip()[:500] if provenance else 'N/A',
            'secao_completa_length': len(secao)
        }
        
        ovos_data.append(ovo_info)
        print(f"✓ Processado: {nome_ovo} ({ano}) - {len(secao)} caracteres")
    else:
        print(f"✗ Não encontrado: {nome_ovo} ({ano})")

# Salvar em JSON
with open('/home/ubuntu/catalogo-faberge/ovos_extraidos.json', 'w', encoding='utf-8') as f:
    json.dump(ovos_data, f, ensure_ascii=False, indent=2)

print(f"\n✓ Total de ovos processados: {len(ovos_data)}/50")
print(f"✓ Dados salvos em: ovos_extraidos.json")
