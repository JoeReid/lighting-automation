from ext.attribute_packer import AttributePackerMixin


class RGBLight(AttributePackerMixin):
    def __init__(self, red=0, green=0, blue=0):
        self.red = red
        self.green = green
        self.blue = blue
        AttributePackerMixin.__init__(self, (
            AttributePackerMixin.Attribute('red', 'onebyte'),
            AttributePackerMixin.Attribute('green', 'onebyte'),
            AttributePackerMixin.Attribute('blue', 'onebyte'),
        ))

    @property
    def rgb(self):
        return (self.red, self.green, self.blue)
    @rgb.setter
    def _rgb_setter(self, rgb):
        self.red, self.green, self.blue = rgb