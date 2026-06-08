import pytest

def test_read_sites_empty(client):
    """Prueba que inicialmente la lista de sitios esté vacía."""
    response = client.get("/sites/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_site_success(client):
    """Prueba la creación exitosa de un sitio (Bypasseando la API Key en la fixture)."""
    site_data = {"name": "Google", "url": "https://google.com"}
    
    # Ya no necesitamos headers especiales porque el conftest hace el bypass
    response = client.post("/sites/", json=site_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Google"
    assert data["url"] == "https://google.com"
    assert "id" in data

def test_list_sites_after_creation(client):
    """Prueba que después de crear un sitio, aparezca en la lista."""
    # 1. Creamos un sitio
    site_data = {"name": "GitHub", "url": "https://github.com"}
    client.post("/sites/", json=site_data)
    
    # 2. Listamos
    response = client.get("/sites/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "GitHub"
