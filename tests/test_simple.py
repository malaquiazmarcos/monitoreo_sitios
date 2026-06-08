from app.models import Site

def test_crear_instancia_site():

    nuevo_sitio = Site(name="Google", url="https://google.com")

    assert nuevo_sitio.name == "Google"
    assert nuevo_sitio.url == "https://google.com"
    assert nuevo_sitio.is_online == True