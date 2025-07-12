# Travel Domain Types
# Extracted from common/types.py for travel-specific implementations

from typing import Any, List, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator


class TripInfo(BaseModel):
    """Trip Info."""

    total_budget: Optional[str] = Field(description='Total Budget for the trip')
    origin: Optional[str] = Field(description='Trip Origin')
    destination: Optional[str] = Field(description='Trip destination')
    type: Optional[str] = Field(description='Trip type, business or leisure')
    start_date: Optional[str] = Field(description='Trip Start Date')
    end_date: Optional[str] = Field(description='Trip End Date')
    travel_class: Optional[str] = Field(
        description='Travel class, first, business or economy'
    )
    accomodation_type: Optional[str] = Field(
        description='Luxury Hotel, Budget Hotel, AirBnB, etc'
    )
    room_type: Optional[str] = Field(description='Suite, Single, Double etc.')
    is_car_rental_required: Optional[str] = Field(
        description='Whether a rental car is required in the trip.'
    )
    type_of_car: Optional[str] = Field(
        description='Type of the car, SUV, Sedan, Truck etc.'
    )
    no_of_travellers: Optional[str] = Field(
        description='Total number of travellers in the trip'
    )

    checkin_date: Optional[str] = Field(description='Hotel Checkin Date')
    checkout_date: Optional[str] = Field(description='Hotel Checkout Date')
    car_rental_start_date: Optional[str] = Field(
        description='Car Rental Start Date'
    )
    car_rental_end_date: Optional[str] = Field(
        description='Car Rental End Date'
    )

    @model_validator(mode='before')
    @classmethod
    def set_dependent_var(cls, values):
        """Pydantic dependent setters."""
        if isinstance(values, dict) and 'start_date' in values:
            values['checkin_date'] = values['start_date']

        if isinstance(values, dict) and 'end_date' in values:
            values['checkout_date'] = values['end_date']

        if isinstance(values, dict) and 'start_date' in values:
            values['car_rental_start_date'] = values['start_date']

        if isinstance(values, dict) and 'end_date' in values:
            values['car_rental_end_date'] = values['end_date']
        return values


class TravelTaskList(BaseModel):
    """Output schema for travel domain planning."""

    original_query: Optional[str] = Field(
        description='The original user query for context.'
    )

    trip_info: Optional[TripInfo] = Field(description='Trip information')

    tasks: List[Any] = Field(
        description='A list of travel tasks to be executed sequentially.'
    )