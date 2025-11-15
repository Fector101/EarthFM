from kivy.graphics import Rectangle, RenderContext
from kivy.metrics import dp
from kivy.properties import ColorProperty, NumericProperty
from kivy.uix.widget import Widget

gradient_shader = """
$HEADER$

uniform vec4  u_color;
uniform float u_fade;

void main()
{
    float x = tex_coord0.x;

    float left_end  = u_fade;         // 0 → fade_width
    float right_end = 1.0 - u_fade;   // 1 → 1-fade_width

    float alpha;

    if (x < left_end) {
        alpha = 1.0 - smoothstep(0.0, left_end, x);
    }
    else if (x > right_end) {
        alpha = smoothstep(right_end, 1.0, x);
    }
    else {
        alpha = 0.0;
    }

    gl_FragColor = vec4(u_color.rgb, min(alpha, u_color[3]));
}
"""


class GradientOverlay(Widget):
    color = ColorProperty([0, 0, 0, 0])
    fade_width = NumericProperty(dp(10))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.canvas = RenderContext(use_parent_projection=True)
        self.canvas.shader.fs = gradient_shader

        with self.canvas:
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(
            pos=self.update_rect,
            size=self.update_rect,
        )

    def on_color(self, instance, color):
        self.canvas["u_color"] = list(float(_) for _ in self.color)

    def on_fade_width(self, instance, fade_width):
        fade_uv = float(fade_width / max(1, self.width))
        self.canvas["u_fade"] = fade_uv

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
