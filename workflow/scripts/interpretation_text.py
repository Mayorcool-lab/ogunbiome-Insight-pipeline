"""
OgunBiome MVP Pipeline — Step 4: Biological Interpretation
Author: Dr. Oluwamayowa Ogun — OgunBiome Insights — CAU Kiel

Expert narrative connecting differential abundance findings to biological
meaning and EFSA regulatory relevance. Written by Dr. Ogun as domain expert.
All interpretations reviewed and approved prior to client delivery.
"""

INTERPRETATIONS = {

    "Bifidobacterium": {
        "what_it_is": (
            "Bifidobacterium is a gram-positive, anaerobic genus within the "
            "phylum Actinobacteria and one of the most well-characterised "
            "health-promoting genera of the human gut microbiome."
        ),
        "what_changed": (
            "Bifidobacterium exhibited a strong increase in relative abundance "
            "of approximately 3.5-fold during inulin supplementation "
            "(adj. p = 0.0022, FDR < 0.05), identifying it as the primary "
            "microbial responder to the intervention."
        ),
        "mechanism": (
            "Bifidobacterium species possess beta-fructosidase enzymes that "
            "specifically cleave the beta-2-1 glycosidic bonds of inulin-type "
            "fructans. This enzymatic capacity positions Bifidobacterium as a "
            "primary degrader of chicory-derived inulin, selectively enriched "
            "through substrate-specific fermentation activity."
        ),
        "health_relevance": (
            "The selective enrichment of Bifidobacterium supports a "
            "mechanistic model in which inulin supplementation enhances both "
            "primary saccharolytic activity and secondary metabolite "
            "production, particularly short-chain fatty acids with established "
            "roles in colonic health, gut barrier integrity, and mucosal "
            "immune regulation."
        ),
        "efsa_relevance": (
            "The enrichment of Bifidobacterium observed here is directly "
            "relevant to EFSA scientific opinions on inulin-type fructans and "
            "gut health biomarkers. EFSA recognises increased Bifidobacterium "
            "abundance as a measurable indicator of prebiotic activity in the "
            "human colon, supporting its use as a functional endpoint in "
            "dietary intervention studies submitted for health claim "
            "substantiation under Regulation EC 1924/2006."
        ),
    },

    "Anaerostipes": {
        "what_it_is": (
            "Anaerostipes is an anaerobic, butyrate-producing genus within "
            "the family Lachnospiraceae, recognised as a key secondary "
            "fermenter in the human gut microbiome."
        ),
        "what_changed": (
            "Anaerostipes showed a significant enrichment of approximately "
            "2.2-fold during inulin supplementation and represented the most "
            "statistically significant finding in the dataset "
            "(adj. p = 0.0001, FDR < 0.05)."
        ),
        "mechanism": (
            "Anaerostipes does not ferment inulin directly. Its enrichment "
            "reflects cross-feeding interactions in which acetate and lactate "
            "produced by Bifidobacterium during inulin fermentation are "
            "utilised by Anaerostipes as substrates for butyrate synthesis "
            "via the acetate-to-butyrate pathway. The concurrent enrichment "
            "of both genera confirms the activation of this cross-feeding "
            "cascade in vivo."
        ),
        "health_relevance": (
            "Butyrate produced by Anaerostipes serves as the primary energy "
            "source for colonocytes and plays a critical role in maintaining "
            "gut barrier integrity, regulating mucosal immune responses, and "
            "suppressing pro-inflammatory signalling pathways. The enrichment "
            "of Anaerostipes provides biologically plausible support for "
            "improved gut metabolic function under inulin supplementation, "
            "consistent with established prebiotic mechanisms."
        ),
        "efsa_relevance": (
            "The enrichment of butyrate-associated taxa observed here is "
            "relevant to EFSA scientific opinions on dietary fibre and gut "
            "health, which recognise short-chain fatty acid production — "
            "particularly butyrate — as a measurable biomarker of prebiotic "
            "activity and a functional indicator of colonic health in human "
            "intervention studies."
        ),
    },

}
