import random
import faker
import csv
import os
import hashlib
from datetime import timedelta

# Inicializa o gerador de dados fictícios
fake = faker.Faker()

# Função para gerar uma hash hexadecimal de 8 caracteres
def generate_hash8():
    full_hash = hashlib.sha256(str(random.random()).encode()).hexdigest()
    return full_hash[:8]

# Função principal
def GenerateData(n, m):
    # Garante que a pasta "Dados" exista
    os.makedirs("Dados", exist_ok=True)

    # Define o caminho do arquivo
    filepath = os.path.join("Dados", "dados_gerados.csv")

    # Gera m hashes únicas
    base_hashes = [generate_hash8() for _ in range(m)]

    # Abre o arquivo para escrita
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Cabeçalhos
        writer.writerow([
            "Hash", "Horário Inicial", "Horário Final",
            "Coordenada 1", "Coordenada 2",
            "Link Imagem", "Câmera"
        ])

        for _ in range(n):
            hash_hex = random.choice(base_hashes)

            # Gera horários
            start_time = fake.date_time_this_year()
            end_time = start_time + timedelta(minutes=random.randint(0, 120))

            # Coordenadas
            coord1 = f"{random.randint(0, 1920)},{random.randint(0, 1080)}"
            coord2 = f"{random.randint(0, 1920)},{random.randint(0, 1080)}"

            # Link fixo (pode ser alterado para fake.url() se quiser variedade)
            link = "https://img.com"

            # Número aleatório de 1 a 100
            number = random.randint(1, 100)

            # Escreve a linha no CSV
            writer.writerow([
                hash_hex,
                start_time.strftime("%H:%M:%S"),
                end_time.strftime("%H:%M:%S"),
                coord1,
                coord2,
                link,
                number
            ])

    print(f"✅ Arquivo gerado com sucesso: {filepath}")

# NDados, NPessoas
GenerateData(20, 4)