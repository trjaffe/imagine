from imagine.fields.field_factory import GeneralFieldFactory
from imagine.fields.test_field.test_field import TestField

class TestFieldFactory(GeneralFieldFactory):

    def __init__(self, boxsize, resolution, active_parameters=tuple()):
        super(TestFieldFactory,self).__init__(boxsize, resolution)
        self.field_type = 1
        self.name = 'test'
        self.field_class = TestField
        self.default_parameters = {'a': 6.0,
                                   'b': 2.0}
        self.parameter_ranges = {'a': self._interval(6.0,2.0,3),
                                 'b': self._positive_interval(2.0,1.0,2.5)}
        self.active_parameters = active_parameters
