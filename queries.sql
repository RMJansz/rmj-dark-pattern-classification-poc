-- SQLite
SELECT COUNT(DISTINCT site_nr) AS skipped_unique_site_nrs FROM patterns WHERE skipped == 1;
SELECT COUNT(DISTINCT site_nr) AS no_patterns__unique_site_nrs FROM patterns WHERE skipped == 0 AND (nooptions + limitedoptions + visualinterfaceinterference) = 0;
SELECT COUNT(DISTINCT site_nr) AS one_pattern_unique_site_nrs FROM patterns WHERE skipped = 0 AND (nooptions + limitedoptions + visualinterfaceinterference) = 1;
SELECT COUNT(DISTINCT site_nr) AS multiple_patterns_unique_site_nrs FROM patterns WHERE skipped = 0 AND (nooptions + limitedoptions + visualinterfaceinterference) >= 2;

SELECT COUNT(DISTINCT site_nr) AS nooptions_unique_site_nrs FROM patterns WHERE skipped == 0 AND nooptions == 1;
SELECT COUNT(DISTINCT site_nr) AS limitedoptions_unique_site_nrs FROM patterns WHERE skipped == 0 AND limitedoptions == 1;
SELECT COUNT(DISTINCT site_nr) AS visualinterfaceinterference_unique_site_nrs FROM patterns WHERE skipped == 0 AND visualinterfaceinterference == 1;

SELECT nooptions AS nooptions_class, COUNT(*) AS count FROM spot_check_validation GROUP BY nooptions;
SELECT limitedoptions AS limitedoptions_class, COUNT(*) AS count FROM spot_check_validation GROUP BY limitedoptions;
SELECT visualinterfaceinterference AS visualinterfaceinterference_class, COUNT(*) AS count FROM spot_check_validation GROUP BY visualinterfaceinterference;