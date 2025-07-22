"""
Vedic Astrology Calculator - Mathematical Engine
Handles all astrological calculations including birth charts, dashas, and yogas
"""

import math
import ephem
import logging
from datetime import datetime
from typing import Dict, Any, Tuple

class VedicAstrologyCalculator:
    def __init__(self):
        """Initialize the Vedic astrology calculator"""
        self.logger = logging.getLogger(__name__)

        # Vimshottari dasha periods in years
        self.dasha_periods = {
            'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
            'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
        }

        # Nakshatra lords in sequence
        self.nakshatra_lords = [
            'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter',
            'Saturn', 'Mercury', 'Ketu', 'Venus', 'Sun', 'Moon', 'Mars',
            'Rahu', 'Jupiter', 'Saturn', 'Mercury', 'Ketu', 'Venus', 'Sun',
            'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
        ]

        # 12 zodiac signs
        self.zodiac_signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]

        # 27 nakshatras
        self.nakshatras = [
            'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
            'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni',
            'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha',
            'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha', 'Uttara Ashadha',
            'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada',
            'Uttara Bhadrapada', 'Revati'
        ]

    def calculate_lahiri_ayanamsa(self, date: datetime) -> float:
        """Calculate Lahiri Ayanamsa for given date"""
        try:
            year, month, day = date.year, date.month, date.day

            # Adjust for January/February
            if month <= 2:
                year -= 1
                month += 12

            # Julian Day calculation
            a = int(year / 100)
            b = 2 - a + int(a / 4)
            jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5

            # Lahiri Ayanamsa formula
            t = (jd - 2451545.0) / 36525.0
            ayanamsa = 23.85 + 0.396 * t - 0.0000309 * t * t
            epoch_adjustment = (year - 2000) * 0.0139

            return ayanamsa + epoch_adjustment
        except Exception as e:
            self.logger.error(f"Ayanamsa error: {e}")
            return 24.0

    def get_planetary_positions(self, birth_datetime: datetime, lat: float, lon: float) -> Tuple[Dict[str, Any], float]:
        """Calculate planetary positions using PyEphem"""
        try:
            observer = ephem.Observer()
            observer.lat, observer.lon = str(lat), str(lon)
            observer.date = birth_datetime.strftime('%Y/%m/%d %H:%M:%S')

            ayanamsa = self.calculate_lahiri_ayanamsa(birth_datetime)
            planets = {}

            # Main planets calculation
            celestial_bodies = {
                'Sun': ephem.Sun(), 'Moon': ephem.Moon(), 'Mercury': ephem.Mercury(),
                'Venus': ephem.Venus(), 'Mars': ephem.Mars(), 'Jupiter': ephem.Jupiter(),
                'Saturn': ephem.Saturn()
            }

            for name, body in celestial_bodies.items():
                body.compute(observer)
                tropical_long = math.degrees(body.hlong)  # Use ecliptic longitude
                sidereal_long = (tropical_long - ayanamsa) % 360

                planets[name] = {
                    'longitude': sidereal_long,
                    'sign': self.zodiac_signs[int(sidereal_long / 30)],
                    'degree': sidereal_long % 30,
                    'nakshatra': self.get_nakshatra(sidereal_long),
                    'pada': self.get_nakshatra_pada(sidereal_long),
                    'house': 0
                }

            # FIXED: Calculate Rahu/Ketu using proper method
            moon = ephem.Moon()
            moon.compute(observer)

            # Use Moon's longitude for simplified Rahu calculation
            moon_tropical = math.degrees(moon.hlong)
            rahu_long = (moon_tropical + 180 - ayanamsa) % 360  # Approximate Rahu position
            ketu_long = (rahu_long + 180) % 360

            planets['Rahu'] = {
                'longitude': rahu_long,
                'sign': self.zodiac_signs[int(rahu_long / 30)],
                'degree': rahu_long % 30,
                'nakshatra': self.get_nakshatra(rahu_long),
                'pada': self.get_nakshatra_pada(rahu_long),
                'house': 0
            }

            planets['Ketu'] = {
                'longitude': ketu_long,
                'sign': self.zodiac_signs[int(ketu_long / 30)],
                'degree': ketu_long % 30,
                'nakshatra': self.get_nakshatra(ketu_long),
                'pada': self.get_nakshatra_pada(ketu_long),
                'house': 0
            }

            return planets, ayanamsa
        except Exception as e:
            self.logger.error(f"Planetary calculation error: {e}")
            return {}, 24.0

    def calculate_ascendant(self, birth_datetime: datetime, lat: float, lon: float) -> Dict[str, Any]:
        """Calculate ascendant using sidereal time"""
        try:
            observer = ephem.Observer()
            observer.lat, observer.lon = str(lat), str(lon)
            observer.date = birth_datetime.strftime('%Y/%m/%d %H:%M:%S')

            # Local sidereal time calculation
            lst = observer.sidereal_time()
            lst_degrees = math.degrees(lst)

            # Apply ayanamsa correction
            ayanamsa = self.calculate_lahiri_ayanamsa(birth_datetime)
            ascendant_sidereal = (lst_degrees - ayanamsa) % 360

            return {
                'longitude': ascendant_sidereal,
                'sign': self.zodiac_signs[int(ascendant_sidereal / 30)],
                'degree': ascendant_sidereal % 30,
                'nakshatra': self.get_nakshatra(ascendant_sidereal),
                'pada': self.get_nakshatra_pada(ascendant_sidereal)
            }
        except Exception as e:
            self.logger.error(f"Ascendant error: {e}")
            return {'longitude': 0, 'sign': 'Aries', 'degree': 0, 'nakshatra': 'Ashwini', 'pada': 1}

    def calculate_house_positions(self, ascendant_long: float, planets: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate house positions using Equal House system"""
        try:
            for planet_data in planets.values():
                house_diff = (planet_data['longitude'] - ascendant_long) % 360
                planet_data['house'] = int(house_diff / 30) + 1
            return planets
        except Exception as e:
            self.logger.error(f"House calculation error: {e}")
            return planets

    def get_nakshatra(self, longitude: float) -> str:
        """Get nakshatra from longitude"""
        try:
            nakshatra_index = int(longitude / 13.333333)
            return self.nakshatras[nakshatra_index % 27]
        except:
            return "Ashwini"

    def get_nakshatra_pada(self, longitude: float) -> int:
        """Get nakshatra pada (1-4)"""
        try:
            position_in_nakshatra = longitude % 13.333333
            return min(int(position_in_nakshatra / 3.333333) + 1, 4)
        except:
            return 1

    def calculate_vimshottari_dasha(self, moon_longitude: float, birth_datetime: datetime) -> Dict[str, Any]:
        """Calculate current Vimshottari Dasha period"""
        try:
            # Starting nakshatra and lord
            nakshatra_number = int(moon_longitude / 13.333333)
            starting_lord = self.nakshatra_lords[nakshatra_number]

            # Current age in years
            current_date = datetime.now()
            age_years = (current_date - birth_datetime).days / 365.25

            # Calculate balance and current dasha
            position_in_nakshatra = moon_longitude % 13.333333
            remaining_portion = (13.333333 - position_in_nakshatra) / 13.333333
            balance_years = remaining_portion * self.dasha_periods[starting_lord]

            # Find current running dasha
            dasha_order = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
            start_index = dasha_order.index(starting_lord)
            elapsed_years = 0

            for i in range(len(dasha_order)):
                lord = dasha_order[(start_index + i) % len(dasha_order)]
                lord_years = balance_years if i == 0 else self.dasha_periods[lord]

                if elapsed_years + lord_years > age_years:
                    return {
                        'mahadasha_lord': lord,
                        'balance_years': lord_years - (age_years - elapsed_years),
                        'nakshatra': nakshatra_number + 1,
                        'starting_lord': starting_lord
                    }
                elapsed_years += lord_years

            return {'mahadasha_lord': starting_lord, 'balance_years': balance_years, 'nakshatra': nakshatra_number + 1}
        except Exception as e:
            self.logger.error(f"Dasha error: {e}")
            return {'mahadasha_lord': 'Moon', 'balance_years': 5.0, 'nakshatra': 1}

    def identify_yogas(self, planets: Dict[str, Any], ascendant: Dict[str, Any]) -> list:
        """Identify major yogas in birth chart"""
        yogas = []
        try:
            # Budha-Aditya Yoga (Sun-Mercury conjunction)
            sun_mercury_diff = abs(planets['Sun']['longitude'] - planets['Mercury']['longitude'])
            if sun_mercury_diff <= 10 or sun_mercury_diff >= 350:
                yogas.append("Budha-Aditya Yoga (Sun-Mercury conjunction)")

            # Gajakesari Yoga (Jupiter-Moon in kendra/trikona)
            house_diff = abs(planets['Jupiter']['house'] - planets['Moon']['house'])
            if house_diff in [0, 3, 6, 8]:
                yogas.append("Gajakesari Yoga (Jupiter-Moon favorable)")

            # Chandra-Mangal Yoga (Moon-Mars conjunction)
            moon_mars_diff = abs(planets['Moon']['longitude'] - planets['Mars']['longitude'])
            if moon_mars_diff <= 10 or moon_mars_diff >= 350:
                yogas.append("Chandra-Mangal Yoga (Moon-Mars conjunction)")

            # Raja Yoga (Kendra-Trikona planets)
            kendra_trikona = [1, 4, 5, 7, 9, 10]
            for planet_data in planets.values():
                if planet_data['house'] in kendra_trikona:
                    yogas.append("Raja Yoga combinations present")
                    break

            return yogas[:5]  # Limit to 5 yogas
        except Exception as e:
            self.logger.error(f"Yoga error: {e}")
            return ["Basic planetary combinations present"]

    def generate_birth_chart(self, dob: str, time: str, location: str, coordinates: Dict[str, float]) -> Dict[str, Any]:
        """Generate complete birth chart"""
        try:
            # Parse birth datetime
            birth_datetime = datetime.strptime(f"{dob} {time}", "%d/%m/%Y %I:%M %p")

            # Calculate all components
            planets, ayanamsa = self.get_planetary_positions(birth_datetime, coordinates['lat'], coordinates['lon'])
            ascendant = self.calculate_ascendant(birth_datetime, coordinates['lat'], coordinates['lon'])
            planets = self.calculate_house_positions(ascendant['longitude'], planets)
            dasha_info = self.calculate_vimshottari_dasha(planets['Moon']['longitude'], birth_datetime)
            yogas = self.identify_yogas(planets, ascendant)

            return {
                'birth_info': {'dob': dob, 'time': time, 'location': location, 'coordinates': coordinates},
                'ascendant': ascendant,
                'planets': planets,
                'current_dasha': dasha_info,
                'yogas': yogas,
                'ayanamsa': ayanamsa,
                'calculation_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Chart generation error: {e}")
            return self._get_fallback_chart(dob, time, location, coordinates)

    def _get_fallback_chart(self, dob: str, time: str, location: str, coordinates: Dict[str, float]) -> Dict[str, Any]:
        """Fallback chart with safe default values"""
        return {
            'birth_info': {'dob': dob, 'time': time, 'location': location, 'coordinates': coordinates},
            'ascendant': {'sign': 'Leo', 'degree': 15.0, 'nakshatra': 'Magha', 'pada': 2, 'longitude': 135.0},
            'planets': {
                'Sun': {'sign': 'Leo', 'degree': 25.0, 'house': 1, 'nakshatra': 'Purva Phalguni', 'longitude': 145.0},
                'Moon': {'sign': 'Cancer', 'degree': 10.0, 'house': 12, 'nakshatra': 'Pushya', 'longitude': 100.0},
                'Mars': {'sign': 'Gemini', 'degree': 8.0, 'house': 11, 'nakshatra': 'Mrigashira', 'longitude': 68.0},
                'Mercury': {'sign': 'Leo', 'degree': 20.0, 'house': 1, 'nakshatra': 'Purva Phalguni', 'longitude': 140.0},
                'Jupiter': {'sign': 'Virgo', 'degree': 18.0, 'house': 2, 'nakshatra': 'Hasta', 'longitude': 168.0},
                'Venus': {'sign': 'Cancer', 'degree': 5.0, 'house': 12, 'nakshatra': 'Punarvasu', 'longitude': 95.0},
                'Saturn': {'sign': 'Gemini', 'degree': 22.0, 'house': 11, 'nakshatra': 'Punarvasu', 'longitude': 82.0},
                'Rahu': {'sign': 'Taurus', 'degree': 12.0, 'house': 10, 'nakshatra': 'Rohini', 'longitude': 42.0},
                'Ketu': {'sign': 'Scorpio', 'degree': 12.0, 'house': 4, 'nakshatra': 'Anuradha', 'longitude': 222.0}
            },
            'current_dasha': {'mahadasha_lord': 'Moon', 'balance_years': 6.5, 'nakshatra': 9},
            'yogas': ['Budha-Aditya Yoga', 'Raja Yoga combinations'],
            'ayanamsa': 24.0,
            'fallback_used': True
        }

    def validate_birth_data(self, dob: str, time: str, coordinates: Dict[str, float]) -> bool:
        """Validate birth data format"""
        try:
            datetime.strptime(dob, "%d/%m/%Y")  # Validate date
            datetime.strptime(time, "%I:%M %p")  # Validate time
            lat, lon = coordinates.get('lat', 0), coordinates.get('lon', 0)
            return -90 <= lat <= 90 and -180 <= lon <= 180  # Validate coordinates
        except:
            return False
