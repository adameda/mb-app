/**
 * Gestion du formulaire de devis avec Alpine.js
 */
function devisForm(lignesExistantes = []) {
    console.log('Initialisation devisForm avec lignes:', lignesExistantes);

    return {
        // Initialisation des lignes existantes ou tableau vide
        lignes: lignesExistantes.length > 0 ? lignesExistantes.map(l => ({
            tache: l.tache || '',
            vehicule: l.vehicule || '',
            description: l.description || '',
            quantite: parseFloat(l.quantite) || 1,
            unite: l.unite || '',
            prix_unitaire_ht: parseFloat(l.prix_unitaire_ht) || 0,
            tva_pourcent: parseFloat(l.tva_pourcent) || 20,
            total_ttc: parseFloat(l.total_ttc) || 0
        })) : [],

        /**
         * Calcule le total HT brut (avant remise)
         */
        get totalHT() {
            return this.lignes.reduce((sum, ligne) => {
                return sum + (ligne.prix_unitaire_ht * ligne.quantite);
            }, 0);
        },

        /**
         * Calcule le montant de la remise
         */
        get remise() {
            const remisePourcent = parseFloat(document.querySelector('[name="remise_pourcent"]')?.value || 0);
            return this.totalHT * (remisePourcent / 100);
        },

        /**
         * Calcule le total HT après application de la remise
         */
        get totalHTApresRemise() {
            return this.totalHT - this.remise;
        },

        /**
         * Calcule le total de la TVA sur le montant après remise
         */
        get totalTVA() {
            const remisePourcent = parseFloat(document.querySelector('[name="remise_pourcent"]')?.value || 0);
            return this.lignes.reduce((sum, ligne) => {
                const montantHT = ligne.prix_unitaire_ht * ligne.quantite;
                const montantHTApresRemise = montantHT * (1 - remisePourcent / 100);
                return sum + (montantHTApresRemise * (ligne.tva_pourcent / 100));
            }, 0);
        },

        /**
         * Calcule le total TTC final
         */
        get totalTTC() {
            return this.totalHTApresRemise + this.totalTVA;
        },

        /**
         * Ajoute une nouvelle ligne vide au devis
         */
        ajouterLigne() {
            this.lignes.push({
                tache: '',
                vehicule: '',
                description: '',
                quantite: 1,
                unite: '',
                prix_unitaire_ht: 0,
                tva_pourcent: 20,
                total_ttc: 0
            });
        },

        /**
         * Supprime une ligne du devis
         * @param {number} index - Index de la ligne à supprimer
         */
        supprimerLigne(index) {
            this.lignes.splice(index, 1);
        },

        /**
         * Calcule les totaux d'une ligne (HT + TVA = TTC)
         * @param {Object} ligne - La ligne à calculer
         */
        calculerLigne(ligne) {
            const montantHT = ligne.prix_unitaire_ht * ligne.quantite;
            const montantTVA = montantHT * (ligne.tva_pourcent / 100);
            ligne.total_ttc = montantHT + montantTVA;
        },

        /**
         * Charge les informations d'un prix depuis le catalogue
         * @param {Object} ligne - La ligne à mettre à jour
         */
        async chargerPrix(ligne) {
            if (!ligne.unite) return;

            try {
                const response = await fetch(`/api/prix/${ligne.unite}`);
                if (response.ok) {
                    const data = await response.json();
                    ligne.prix_unitaire_ht = data.prix;
                    ligne.description = data.description || '';
                    ligne.tache = data.categorie === 'TOLERIE_CARROSSERIE'
                        ? 'TOLERIE_CARROSSERIE'
                        : 'DEBOSSELAGE';

                    // Appliquer TVA par défaut si non définie
                    if (!ligne.tva_pourcent || ligne.tva_pourcent === 0) {
                        ligne.tva_pourcent = 20;
                    }

                    this.calculerLigne(ligne);
                } else {
                    console.error(`Prix non trouvé pour le code: ${ligne.unite}`);
                }
            } catch (error) {
                console.error('Erreur lors du chargement du prix:', error);
            }
        },

        /**
         * Validation avant soumission du formulaire
         * @param {Event} e - L'événement de soumission
         */
        onSubmit(e) {
            if (this.lignes.length === 0) {
                e.preventDefault();
                alert('Veuillez ajouter au moins une ligne au devis.');
                return false;
            }
        }
    }
}
