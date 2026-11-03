#> Sampled exterior-ocean contact. The probe offsets are unchanged; only the
#> reaction depends on the round phase.
execute positioned ~-0.299 ~-0.01 ~-0.299 if block ~ ~ ~ #meridian_base:ocean run return run function meridian_base:ocean_contact
execute positioned ~-0.299 ~-0.01 ~0.299 if block ~ ~ ~ #meridian_base:ocean run return run function meridian_base:ocean_contact
execute positioned ~0.299 ~-0.01 ~-0.299 if block ~ ~ ~ #meridian_base:ocean run return run function meridian_base:ocean_contact
execute positioned ~0.299 ~-0.01 ~0.299 if block ~ ~ ~ #meridian_base:ocean run return run function meridian_base:ocean_contact
execute positioned ~0 ~-0.01 ~0 if block ~ ~ ~ #meridian_base:ocean run return run function meridian_base:ocean_contact
