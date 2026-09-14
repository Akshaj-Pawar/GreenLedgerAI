
# general purpose unit conversion functions

from pint import UnitRegistry

ureg = UnitRegistry()

# same for all units defined
ureg.define("CO2e = [co2e]")
ureg.define("kg_CO2e = 1 * CO2e")

def normalise_unit_string(unit: str) -> str:
    # to be called when ef units are involved
    return (
        unit.strip()
        .replace(" per ", "/")
    )

# estimation algorithsm

def scope2_fub_get_ef(site_location_city, site_postcode, merchant_name, product, cost, currency, start_date, end_date):
    # may as well add a real algorithm and return emissions as well as emissions factor
    # literally why doesn't it require kwhs
    # if electricity, trace emissions factor from location via api call
    ef = 1
    emissions = 1
    return ef, emissions

def scope1_get_combustion_emissions(fuel_type, fuel_brand, quantity_consumed_mass, unit_mass, quantity_consumed_vol, unit_vol, carbon_content, NCV_value, dryness_basis, fuel_quality_certification, energy_produced_overall, unit_energy, reporting_period, consumption_process, site_name, site_owner):
    # dryness basis = ARB / ADB / DB
    
    def get_ef_by_energy(fuel_type, fuel_brand, dryness_basis):
        # find online dataset(s) that provide values in given quant type, download, make into a dictionary of endpoints to call or something
        # associate it with the units
        # figure out how to query given fuel_type
        # store list of fuel types / ids somewhere along with known aliases so when designed the LLM phase it knows the possible values (maybe via RAG but that's a problem for later)
        # this is actually not that hard

        ef = 1
        ef_unit = None

        return ef, ef_unit

    def analyse_fuel(fuel_type, fuel_brand):

        carbon_content_est = 1
        oxidation_factor = 1

        return carbon_content_est, oxidation_factor


    def find_std_ef_mass(fuel_type, fuel_brand, quant_type):
        ef = 1
        ef_unit = None
        return ef, ef_unit

    def find_std_ef_vol(fuel_type, fuel_brand, quant_type):
        ef = 1
        ef_unit = None
        return ef, ef_unit

    default_ef = 1 # placeholder value

    # using fuel type, retrieve net caloric value and oxidation factor if applicable

    if energy_produced_overall is not None and unit_energy is not None and NCV_value is not None and dryness_basis is not None:

        method = "energy_based_estimate"
        ef_val, ef_unit = get_ef_by_energy(fuel_type, fuel_brand, dryness_basis)
        ef_unit = normalise_unit_string(ef_unit)

        ef = ureg.Quantity(ef_val, ef_unit).to("kg_CO2e/kwh")
        energy_produced = ureg.Quantity(energy_produced_overall, unit_energy).to("kwh")

        # normalise layer, convert ef to the correct units

        carbon_output = (NCV_value * ef * energy_produced).magnitude

        new_ef_val = ef.magnitude
        new_ef_units = ef.units

    else:
        if fuel_type is not None:

            if quantity_consumed_mass is not None and unit_mass is not None:

                # some fuels have known efs
                method = "carbon_counting_via_known_ef"
                ef_val, ef_unit = find_std_ef_mass(fuel_type, fuel_brand, quant_type="mass")
                ef_unit = normalise_unit_string(ef_unit)

                ef = ureg.Quantity(ef_val, ef_unit).to("kg_CO2e/kg")
                mass_consumed = ureg.Quantity(quantity_consumed_mass, unit_mass).to("kg")

                # normalise-ation layer to get ef per unit mass

                carbon_output = (mass_consumed * ef).magnitude

                new_ef_val = ef.magnitude
                new_ef_units = ef.units

            elif quantity_consumed_vol is not None and unit_vol is not None:

                method = "carbon_counting_via_known_ef"

                # some fuels have known efs
                ef, ef_unit = find_std_ef_vol(fuel_type, fuel_brand, quant_type="vol")
                ef_unit = normalise_unit_string(ef_unit)

                ef = ureg.Quantity(ef_val, ef_unit).to("kg_CO2e/l")
                vol_consumed = ureg.Quantity(quantity_consumed_vol, unit_vol).to("litres")

                carbon_output = (vol_consumed * ef).magnitude
                new_ef_val = ef.magnitude
                new_ef_units = ef.units

                # normalise-ation layer to het ef per unit volume
            
            else:
                # fail
                method = None
                ef = None
                ef_units = None
                carbon_output = None

                return method, ef, ef_units, carbon_output

            if ef is None and quantity_consumed_mass is not None and unit_mass is not None:

                method = "carbon_counting_via_estimated_ef" # override method

                carbon_content_est, oxidation_factor = analyse_fuel(fuel_type, fuel_brand)

                mass_consumed = ureg.Quantity(quantity_consumed_mass, unit_mass).to("kg")

                if carbon_content is None:
                    carbon_content = carbon_content_est
                    # otherwise as provided by the documentation

                ef = carbon_content * oxidation_factor * 44/12   # otherwise as calculated by find_std_ef
                carbon_output = (mass_consumed * ef).magnitude

                new_ef_val = ef
                new_ef_units = "kgco2e/kg"

        else:
            # fail
            method = None
            ef = None
            ef_units = None
            carbon_output = None

            return method, ef, ef_units, carbon_output

        # other kyoto gas outputs?

        return method, new_ef_val, new_ef_units, carbon_output

#def scope1_get_process_emissions():
#    # niche
#    return 1

def scope1_get_fugitive_emissions_refridgerant(refrigerant_type, leaked_refrigerant_vol, units_vol, leaked_refrigerant_mass, units_mass):

    def call_gwp_api_mass(refrigerant_type):
        # find online dataset for gwp, download
        # figure out how to query given refridgerant type
        # store list of refrigerant types / ids somewhere along with known aliases so when designed the LLM phase it knows the possible values (maybe via RAG but that's a problem for later)
        # this is actually not that hard
        gwp = 1
        return gwp

    def call_gwp_api_vol(refrigerant_type):
        gwp = 1
        return gwp

    if refrigerant_type is not None:
        if leaked_refrigerant_mass is not None and units_mass is not None:
            gwp = call_gwp_api_mass(refrigerant_type)

            mass_leaked = ureg.Quantity(leaked_refrigerant_mass, units_mass).to("kg")

            # normalise for unit
            method = 'via gwp of refridgerant'
            emissions = (gwp * mass_leaked).magnitude

        if leaked_refrigerant_vol is not None and units_vol is not None:
            gwp = call_gwp_api_vol(refrigerant_type)

            vol_leaked = ureg.Quantity(leaked_refrigerant_vol, units_vol).to("litres")

            # normalise for unit
            method = 'via gwp of refrigerant'
            emissions = (gwp * vol_leaked).magnitude
    else:
        method = None
        gwp = None
        emissions = None
    return method, gwp, emissions

def scope3_spend_estimate_production(cost, currency, quantity_bought, unit_of_quantity_bought, product_category, year_purchased, declared_emissions_per_unit_product, unit_wrt_declared_emissions):

    def get_eeiof():
        return 1

    def get_ef_product():
        return 1

    def normalise_cost_to_usd(cost):
        # also deflates to a standard year
        return cost


    if declared_emissions_per_unit_product is not None:
        # must convert quantity bought into standard units (unit_wrt_declared_emissions)
        emissions = declared_emissions_per_unit_product * quantity_bought
        ef = declared_emissions_per_unit_product
        method = f"via declared emissions per {unit_wrt_declared_emissions} product"

    elif (quantity_bought is not None) and (product_category is not None):
        method = "quantity based estimate"
        ef = get_ef_product(quantity_bought, product_category)
        emissions = quantity_bought * ef
        # NOTE: confusion as to how exactly the api calls work and what fields can be used to get what measures

    elif (cost is not None) and (currency is not None) and (product_category is not None):
        norm_cost = normalise_cost_to_usd(cost)
        if year_purchased is None:
            year_purchased = "current year" # change so it actually returns the current year
        eeiof = get_eeiof(cost, currency, product_category, year_purchased)
        method = "spend estimate"
        ef = eeiof
        emissions = norm_cost * ef

    else:
        method = None
        ef = None
        emissions = None

    return method, ef, emissions

def scope3_spend_estimate_transportation(cost, currency, transport_mode, distance, tonnage):
    # normalise cost to set currency
    # idk what the function for this is
    if True: # if whatever is needed is present NOTE: what is needed is not known
        pass
    else:
        method = None
        ef = None
        emissions = None

    return method, ef, emissions


# scope 1:

# da infrastructure
# scope 2: write out scope2 alg

# fiddle with databases
# data handlers
# add api calls (complicated)

# chunking situation
# vectorisation + prompt eng

# LLM call non agentic

# scope 3: verify assumptions via AI, write out transport scope3
# fill in the conversion blanks
# more sophisticated system using dictionaries or objects to store

# system logical pitfall analysis
# testing and eval stage


# LLM call agentic??
# kyoto gas breakdowns
# using density to convert? Or ask the AI to do that?
# expand datasets via countries of different origin