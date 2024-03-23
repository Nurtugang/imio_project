from pvbalch_constants import *


class Compound:
    """
    Initializes a Compound object with weights of elements.
    Au and Ag parameters must be given in grams, other elements in percentage form.
    After initialization, Au and Ag will be converted into grams per ton, while other elements will be converted into their weight in grams based on the compound's total weight.
    
    Parameters:
    - Weight: The total weight of the compound.
    - **elements: A variable number of keyword arguments representing element percentages or weights. Au and Ag are expected in grams, other elements in percentages.
    """
    def __init__(self, **data):
        self.Weight = data.pop('Weight')
        self.elements = {k: self.calc_weight_tonn(v) if k in ['Au', 'Ag'] else self.calc_weight(v)
                         for k, v in data.items()}
        # Assuming 'Other' is not explicitly provided and is calculated as 100% minus the sum of provided percentages.
        self.elements['Other'] = self.calc_weight(100 - sum(v for k, v in data.items() if k not in ['Au', 'Ag']))

    def calc_weight(self, percent):
        """Converts a percentage into a weight based on the total weight of the compound."""
        return round(self.Weight * percent / 100, 2)

    def calc_weight_tonn(self, grams):
        """Converts grams into grams per ton based on the total weight of the compound."""
        return grams / self.Weight if self.Weight else 0


def calculate_total_elements(compounds):
    """
    Calculates the total amount of each element across given Compound objects.

    :param compounds: Variable number of Compound objects.
    :return: A dictionary with elements as keys and their total amounts as values.
    """
    total_elements = {}
    for compound in compounds:
        for element, value in compound.elements.items():
            if element in total_elements:
                total_elements[element] += value
            else:
                total_elements[element] = value
    return total_elements

def calculate_element_percentages(total_elements, total_weight):
    """
    Calculates the sum of each element across all given Compound objects and
    the percentage of each element's sum relative to the total weight.

    :param compounds: Variable number of Compound objects.
    :return: A dictionary with element names as keys and their percentage contribution as values.
    """
    element_percentages = {k: v*1_000_000/total_weight if k in ['Au', 'Ag'] else v*100/total_weight
                         for k, v in total_elements.items()}
    return element_percentages

def calculate_materials_in_stein(total_elements, total_weight, element_percentages):
    """
    Calculate the concentration of materials in the stein and the total weight of the stein.
    """
    sulfur_in_gas = total_elements['S'] * (100 - GAS_LOSS_PERCENTAGE) / 100
    copper_sulfide_sulfur = total_elements['Cu'] * COPPER_TO_SULFUR_RATIO_IN_COPPER_SULFIDE
    sulfur_in_stein = sulfur_in_gas - copper_sulfide_sulfur
    iron_in_stein = sulfur_in_stein * IRON_TO_SULFUR_RATIO_IN_IRON_SULFIDE
    iron_in_slag = total_weight * element_percentages['Fe'] / 100 - iron_in_stein
    print(total_elements['Fe'])
    iron_oxide_in_slag = iron_in_slag * IRON_OXIDE_TO_IRON_RATIO_IN_SLAG
    stein_weight = total_elements['Cu'] + copper_sulfide_sulfur + iron_in_stein + sulfur_in_stein + OTHER_MATERIAL_FACTOR * total_elements['Other']

    return {
        'stein_weight': stein_weight,
        'Cu_in_stein_percentage': total_elements['Cu'] / stein_weight * 100,
        'Fe_in_stein_percentage': iron_in_stein / stein_weight * 100,
        'S_in_stein_percentage': sulfur_in_gas / stein_weight * 100,
        'iron_in_slag':iron_in_slag,
        'iron_oxide_in_slag': iron_oxide_in_slag
    }



def calculate_materials_in_slug(total_elements, stein_results):
    """
    Calculate the concentration of gold, silver and others in the stein and the total weight of the slag.
    """
    # Calculate gold and silver concentration in the stein
    gold_concentration_stein = (total_elements['Au'] / stein_results['stein_weight'] * GOLD_RECOVERY_EFFICIENCY) * GOLD_SILVER_SCALE_FACTOR
    silver_concentration_stein = (total_elements['Ag'] / stein_results['stein_weight'] * SILVER_RECOVERY_EFFICIENCY) * GOLD_SILVER_SCALE_FACTOR

    # Calculate the total weight of the slag
    slag_weight = (
        stein_results['iron_in_slag'] +
        total_elements['Al2O3'] +
        total_elements['SiO2'] +
        total_elements['CaO'] +
        total_elements['Other'] * OTHER_MATERIALS_IN_SLAG_FACTOR
    )

    return {
        'gold_concentration_stein': gold_concentration_stein,
        'silver_concentration_stein': silver_concentration_stein,
        'SiO2_in_slag_percentage': total_elements['SiO2'] / slag_weight * 100,
        'CaO_in_slag_percentage': total_elements['CaO'] / slag_weight * 100,
        'Al2O3_in_slag_percentage': total_elements['Al2O3'] / slag_weight * 100,
        'FeO_in_slag_percentage': stein_results['iron_oxide_in_slag'] / slag_weight * 100,
        'slag_weight': slag_weight,
    }