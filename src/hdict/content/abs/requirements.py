class withRequirements:
    _requirements = None
    fargs: dict
    fkwargs: dict

    @property
    def requirements(self):
        """Requirements (dependencies stub) are alphabetically sorted to ensure we keep the same resulting hosh no matter in which order the parameters are defined in the function"""
        if self._requirements is None:
            self._requirements = {k: v for k, v in sorted((self.fargs | self.fkwargs).items())}
        return self._requirements
