import logging
from .models import PageView
from ipware import get_client_ip
from django.contrib.gis.geoip2 import GeoIP2
from urllib.parse import urlparse
import user_agents

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_source_from_referrer(referrer):
    if not referrer:
        return "Direto"
    parsed_uri = urlparse(referrer)
    domain = parsed_uri.netloc
    if 'google' in domain: return 'Google'
    if 'linkedin' in domain: return 'LinkedIn'
    if 'github' in domain: return 'GitHub'
    if 'facebook' in domain: return 'Facebook'
    if domain == 't.co': return 'Twitter'
    return domain


def save_detailed_page_view(request):
    try:
        ip, _ = get_client_ip(request)
        if ip:
            ua_string = request.META.get('HTTP_USER_AGENT', '')
            user_agent = user_agents.parse(ua_string)
            referrer = request.META.get('HTTP_REFERER')

            page_view = PageView(
                ip_address=ip,
                user_agent=ua_string,
                referrer=referrer,
                source=get_source_from_referrer(referrer),
                operating_system=user_agent.os.family,
                browser=user_agent.browser.family,
            )

            try:
                g = GeoIP2()
                city_data = g.city(ip)
                page_view.country = city_data.get('country_name')
                page_view.city = city_data.get('city')
                page_view.region = city_data.get('region')
            except Exception:
                pass

            page_view.save()
            print(f"PageView salvo para o IP: {ip}")
    except Exception as e:
        print(f"Erro ao salvar PageView: {e}")
