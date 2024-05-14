from flask import current_app
import json
from backend.exceptions import NotFound
from backend.models.dtos.partner_dto import (
    PartnerDTO
)
from backend.models.postgis.partner import (
    Partner
)


class PartnerServiceError(Exception):
    """Custom Exception to notify callers an error occurred when handling partners"""

    def __init__(self, message):
        if current_app:
            current_app.logger.debug(message)

class PartnerService:
    @staticmethod
    def get_partner_by_id(partner_id: int) -> Partner:
        partner = Partner.get_by_id(partner_id)

        if partner is None:
            raise NotFound(
                sub_code="PARTNER_NOT_FOUND", partner_id=partner_id
            )     
      
        return partner

    @staticmethod
    def get_partner_by_permalink(permalink: str)-> Partner:
        partner = Partner.get_by_permalink(permalink)

        if partner is None:
            raise NotFound(
                sub_code="PARTNER_NOT_FOUND", permalink=permalink
            )     
      
        return partner

    
    @staticmethod
    def create_partner(data):
        """Create a new partner in database"""
        website_links = []
        for i in range(1, 6):
            name_key = f"name_{i}"
            url_key = f"url_{i}"
            name = data.get(name_key)
            url = data.get(url_key)
            if name and url:
                website_links.append({"name": name, "url": url})

        new_partner = Partner(
            name=data.get("name"),
            primary_hashtag=data.get("primary_hashtag"),
            secondary_hashtag=data.get("secondary_hashtag"),
            logo_url=data.get("logo_url"),
            link_meta=data.get("link_meta"),
            link_x=data.get("link_x"),
            link_instagram=data.get("link_instagram"),
            current_projects=data.get("current_projects"),
            permalink=data.get("permalink"),
            website_links=json.dumps(website_links)
        )
        new_partner.create()
        return new_partner

    @staticmethod
    def delete_partner(partner_id: int):
        partner = Partner.get_by_id(partner_id)

        if partner:
            partner.delete()
            return {"Success": "Team deleted"}, 200
        else:
            return {
                "Error": "Partner cannot be deleted",
            }, 400
        
    def update_partner(partner_id: int, data: dict) -> Partner:
        partner = Partner.get_by_id(partner_id)
        if not partner:
            raise NotFound(sub_code="PARTNER_NOT_FOUND", partner_id=partner_id)
        
        website_links = []
        for key, value in data.items():
            if key.startswith("name_"):
                index = key.split("_")[1]
                url_key = f"url_{index}"
                if url_key in data and value.strip():
                    website_links.append({"name": value, "url": data[url_key]})

        for key, value in data.items():
            if  hasattr(partner, key):
                setattr(partner, key, value)
        
        partner.website_links = json.dumps(website_links)
        partner.save()
        return partner

    @staticmethod
    def get_partner_dto_by_id(partner: int, request_partner: int) -> PartnerDTO:
        partner = PartnerService.get_partner_by_id(partner)
        if request_partner:
            request_name = PartnerService.get_partner_by_id(request_partner).name
            return partner.as_dto(request_name)
        return partner.as_dto()

    @staticmethod
    def get_all_partners():
        """Get all partners"""
        return Partner.get_all_partners()
    