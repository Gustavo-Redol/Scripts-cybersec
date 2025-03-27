import shodan

def buscar_eternalblue(api_key, output_file="eternalblue_vuln.txt"):
    try:
        api = shodan.Shodan(api_key)
        query = "port:445 os:"windows""  # Busca máquinas Windows com SMB exposto
        results = api.search(query)
        
        with open(output_file, "w") as f:
            for result in results["matches"]:
                ip = result["ip_str"]
                hostnames = result.get("hostnames", [])
                
                f.write(ip)
                if hostnames:
                    f.write(" - " + ", ".join(hostnames))
                f.write("\n")
                
                print(f"Encontrado: {ip} - {', '.join(hostnames) if hostnames else 'Sem domínio'}")
        
        print(f"Resultados salvos em {output_file}")
    except shodan.APIError as e:
        print(f"Erro na API do Shodan: {e}")

if __name__ == "__main__":
    API_KEY = "SUA_SHODAN_API_KEY"  # Substitua pela sua chave de API do Shodan
    buscar_eternalblue(API_KEY)
