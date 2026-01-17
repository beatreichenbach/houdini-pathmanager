        # Replace
        form = ParameterForm('replace')
        self.forms[ModifyMethod.REPLACE] = form

        parm = StringParameter('search')
        form.add_parameter(parm)

        parm = StringParameter('replace')
        form.add_parameter(parm)

        parm = BoolParameter('regex')
        form.add_parameter(parm)

        parm = BoolParameter('match_case')
        form.add_parameter(parm)


        # Copy / Move
        form = ParameterForm('copy')
        self.forms[ModifyMethod.COPY] = form

        parm = HoudiniPathParameter('destination')
        parm.set_method(HoudiniPathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm)

        parm = HoudiniPathParameter('relative_root')
        parm.set_method(HoudiniPathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm, checkable=True)

        # Move
        form = ParameterForm('move')
        self.forms[ModifyMethod.MOVE] = form

        parm = HoudiniPathParameter('destination')
        parm.set_method(HoudiniPathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm)

        parm = HoudiniPathParameter('relative_root')
        parm.set_method(HoudiniPathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm, checkable=True)

        # Find
        form = ParameterForm('find')
        self.forms[ModifyMethod.FIND] = form

        parm = HoudiniPathParameter('root')
        parm.set_method(HoudiniPathParameter.Method.EXISTING_DIR)
        parm.set_default('$HIP')
        form.add_parameter(parm)

        # Version
        form = ParameterForm('version')
        self.forms[ModifyMethod.VERSION] = form

        parm = IntParameter('version')
        parm.set_slider_visible(False)
        parm.set_default(-1)
        form.add_parameter(parm)

        parm = StringParameter('pattern')
        parm.set_default('v(\d+)')
        form.add_parameter(parm)

        # Anchor
        form = ParameterForm('relative')
        self.forms[ModifyMethod.RELATIVE] = form

        parm = HoudiniEnumParameter('anchor')
        parm.set_enum(AnchorMethod)
        parm.set_formatter(formatter)
        form.add_parameter(parm)

        method_parm = parm

        parm = IntParameter('parents')
        parm.set_line_min(0)
        parm.set_slider_visible(False)
        form.add_parameter(parm)

        method_parm.value_changed.connect(
            lambda m, p=parm: p.setEnabled(
                m in (AnchorMethod.RELATIVE_HIP, AnchorMethod.RELATIVE_JOB)
            )
        )