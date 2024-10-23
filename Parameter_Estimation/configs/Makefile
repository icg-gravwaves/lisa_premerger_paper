CONFIG = config.mk
include ${CONFIG}

PSDS = optimistic pessimistic cut

$(PSDS):
	python generate_injection_files.py \
		--outdir ${INJECTION_PATH}/$@_psd/ \
		--config-path ${CONFIG_PATH}/ \
		--injection-file ${INJECTION_FILE} \
		--f-lower-file ${FLOWER_FILE} \
		--psd-file ${CONFIG_PATH}/psds_$@.ini \
		--data-files ${DATAFILES_PATH}/data_$@_psd/ \
		--data-files-label ${DATAFILES_LABEL}

.PHONY: create_ini_files
create_ini_files : 
	@$(MAKE) $(PSDS)

.PHONY: clean_ini_files
clean_ini_files : 
	rm -r ${INJECTION_PATH}
