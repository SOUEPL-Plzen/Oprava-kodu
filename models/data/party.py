"""Tabulka parties. Fyzická a právnická osoba jsou potomci jednoho odběratele."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.data.base import Entity, Timestamped, table_args
from models.data.mixins import AddressMixin, OrganizationMixin


class Party(AddressMixin, OrganizationMixin, Timestamped, Entity):
    __tablename__ = "parties"
    __table_args__ = table_args()

    kind: Mapped[str] = mapped_column(String(16))
    first_name: Mapped[str] = mapped_column(String(128), default="", server_default="")
    last_name: Mapped[str] = mapped_column(String(128), default="", server_default="")

    __mapper_args__ = {"polymorphic_on": "kind", "polymorphic_identity": "party"}

    def person_kwargs(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "company_name": self.company_name,
            "ico": self.ico,
            "dic": self.dic,
            "street": self.street,
            "city": self.city,
            "zip_code": self.zip_code,
            "country": self.country,
            "email": self.email,
            "phone": self.phone,
        }

    def to_dto(self):
        if self.kind == "pravnicka":
            return LegalEntity.to_dto(self)
        return NaturalPerson.to_dto(self)


class NaturalPerson(Party):
    """Fyzická osoba, včetně OSVČ."""

    __mapper_args__ = {"polymorphic_identity": "fyzicka"}

    def to_dto(self):
        from domain.entities import NaturalPersonCard

        return NaturalPersonCard(**self.person_kwargs())


class LegalEntity(Party):
    """Právnická osoba."""

    __mapper_args__ = {"polymorphic_identity": "pravnicka"}

    def to_dto(self):
        from domain.entities import LegalEntityCard

        return LegalEntityCard(**self.person_kwargs())
