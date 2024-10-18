CONFIG = config.mk
include ${CONFIG}

PSDS = optimistic pessimistic cut

generate_data:
	@$(MAKE) $(PSDS)

$(PSDS):
	python generate_data.py \
		--configs base_data.ini psds_$@.ini \
		--injections-file ${INJECTIONS_FILE} \
		--outdir ${DATA_DIR}/data_$@_psd/ \
		--label signal
	python generate_data.py \
		--configs base_data.ini psds_$@.ini \
		--injections-file ${INJECTIONS_FILE} \
		--outdir ${DATA_DIR}/data_$@_psd/ \
		--label signal_zero_noise \
		--zero-noise

.PHONY: generate_data $(LABELS)
