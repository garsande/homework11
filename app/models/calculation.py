# app/models/calculation.py
#Calculation Models with Polymorphic Inheritance


from datetime import datetime
from uuid import uuid4
from typing import List
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declared_attr
from app.database import Base

class AbstractCalculation:
    #Abstract base class defining common attributes for all calculations.
    __tablename__ = "calculations"
    
    @declared_attr
    def id(cls):
        """Unique identifier for each calculation (UUID for distribution)"""
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid4,
            nullable=False
        )

    @declared_attr
    def user_id(cls):
        """
        Foreign key to the user who owns this calculation.
        
        CASCADE delete ensures calculations are deleted when user is deleted.
        Index improves query performance when filtering by user_id.
        """
        return Column(
            UUID(as_uuid=True),
            ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
            index=True
        )

    @declared_attr
    def type(cls):
        """
        Discriminator column for polymorphic inheritance.
        
        This column tells SQLAlchemy which subclass to instantiate when
        loading records from the database. Values include: 'addition',
        'subtraction', 'multiplication', 'division'.
        """
        return Column(
            String(50),
            nullable=False,
            index=True
        )

    @declared_attr
    def inputs(cls):
        """
        JSON column storing the list of numbers for the calculation.
        
        Using JSON allows for flexible storage of variable-length input lists.
        PostgreSQL's native JSON support provides efficient querying and
        indexing capabilities.
        """
        return Column(
            JSON,
            nullable=False
        )

    @declared_attr
    def result(cls):
        """
        The computed result of the calculation.
        
        Stored as Float to handle decimal values. Can be NULL initially
        and computed on-demand using get_result() method.
        """
        return Column(
            Float,
            nullable=True
        )

    @declared_attr
    def created_at(cls):
        """Timestamp when the calculation was created"""
        return Column(
            DateTime,
            default=datetime.utcnow,
            nullable=False
        )

    @declared_attr
    def updated_at(cls):
        """Timestamp when the calculation was last updated"""
        return Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False
        )

    @declared_attr
    def user(cls):
        """
        Relationship to the User model.
        
        back_populates creates a bidirectional relationship, allowing access
        to user.calculations and calculation.user.
        """
        return relationship("User", back_populates="calculations")
    
    @classmethod
    def create(cls, calculation_type: str, user_id: uuid4,
               inputs: List[float]) -> "Calculation":
       # Factory method to create the appropriate calculation subclass.
        calculation_classes = {
            'addition': Addition,
            'subtraction': Subtraction,
            'multiplication': Multiplication,
            'division': Division,
        }
        normalized_type = calculation_type.lower()
        calculation_class = calculation_classes.get(normalized_type)
        if not calculation_class:
            raise ValueError(
                f"Unsupported calculation type: {calculation_type}"
            )
        return calculation_class(user_id=user_id, inputs=inputs)

    def get_result(self) -> float:
        #Abstract method to compute the calculation result.
        
        raise NotImplementedError(
            "Subclasses must implement get_result() method"
        )

    def __repr__(self):
        return f"<Calculation(type={self.type}, inputs={self.inputs})>"


class Calculation(Base, AbstractCalculation):
    #Base calculation model with polymorphic configuration.
    
    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "calculation",
    }


class Addition(Calculation):
    #Addition calculation subclass.
    __mapper_args__ = {"polymorphic_identity": "addition"}

    def get_result(self) -> float:
        if not isinstance(self.inputs, list):
            raise ValueError("Inputs must be a list of numbers.")
        if len(self.inputs) < 2:
            raise ValueError(
                "Inputs must be a list with at least two numbers."
            )
        return sum(self.inputs)


class Subtraction(Calculation):
    #Subtraction calculation subclass.
    __mapper_args__ = {"polymorphic_identity": "subtraction"}

    def get_result(self) -> float:
        if not isinstance(self.inputs, list):
            raise ValueError("Inputs must be a list of numbers.")
        if len(self.inputs) < 2:
            raise ValueError(
                "Inputs must be a list with at least two numbers."
            )
        result = self.inputs[0]
        for value in self.inputs[1:]:
            result -= value
        return result


class Multiplication(Calculation):
    #Multiplication calculation subclass.
    __mapper_args__ = {"polymorphic_identity": "multiplication"}

    def get_result(self) -> float:
        if not isinstance(self.inputs, list):
            raise ValueError("Inputs must be a list of numbers.")
        if len(self.inputs) < 2:
            raise ValueError(
                "Inputs must be a list with at least two numbers."
            )
        result = 1
        for value in self.inputs:
            result *= value
        return result


class Division(Calculation):
    #Division calculation subclass.
    __mapper_args__ = {"polymorphic_identity": "division"}

    def get_result(self) -> float:
        if not isinstance(self.inputs, list):
            raise ValueError("Inputs must be a list of numbers.")
        if len(self.inputs) < 2:
            raise ValueError(
                "Inputs must be a list with at least two numbers."
            )
        result = self.inputs[0]
        for value in self.inputs[1:]:
            if value == 0:
                raise ValueError("Cannot divide by zero.")
            result /= value
        return result
