MATH_GEO_LOW = {
    "problem": "In right triangle $ABC$, shown below, $\\cos{B}=\\frac{6}{10}$.  What is $\\tan{C}$?\n\n[asy]\ndraw((0,0)--(10,0)--(3.6,4.8)--cycle,black+linewidth(1));\ndraw(rightanglemark((0,0),(3.6,4.8),(10,0),20),black+linewidth(1));\nlabel(\"$C$\",(10,0),E);\nlabel(\"$A$\",(3.6,4.8),N);\nlabel(\"$B$\",(0,0),W);\nlabel(\"10\",(0,0)--(10,0),S);\n[/asy]",
    "level": "Level 2",
    "type": "frac34",
    "solution": "Since $\\cos{B}=\\frac{6}{10}$, and the length of the hypotenuse is $BC=10$, $AB=6$.  Then, from the Pythagorean Theorem, we have \\begin{align*}AB^2+AC^2&=BC^2 \\\\ \\Rightarrow\\qquad{AC}&=\\sqrt{BC^2-AB^2} \\\\ &=\\sqrt{10^2-6^2} \\\\ &=\\sqrt{64} \\\\ &=8.\\end{align*}Therefore, $\\tan{C}=\\frac{AB}{AC}=\\frac{6}{8} = \\boxed{\\frac34}$."
}

MATH_GEO_MIDDLE = {
    "problem": "A triangle with sides $3a-1$, $a^2 + 1$ and $a^2 + 2$ has a perimeter of 16 units. What is the number of square units in the area of the triangle?",
    "level": "Level 3",
    "type": "Geometry",
    "answer" : "12 units",
    "solution": "Sum $3a-1$, $a^2+1$, and $a^2+2$ to find $2a^2+3a+2=16$.  Subtract 16 from both sides and factor the left-hand side to find $(2a+7)(a-2)=0\\implies a=-7/2$ or $a=2$.  Discarding the negative solution, we substitute $a=2$ into $3a-1$, $a^2+1$, and $a^2+2$ to find that the side lengths of the triangle are 5, 5, and 6 units.  Draw a perpendicular from the 6-unit side to the opposite vertex to divide the triangle into two congruent right triangles (see figure).  The height of the triangle is $\\sqrt{5^2-3^2}=4$ units, so the area of the triangle is $\\frac{1}{2}(6)(4)=\\boxed{12\\text{ square units}}$.\n\n[asy]\nimport olympiad;\nsize(150);\ndefaultpen(linewidth(0.8)+fontsize(10));\npair A=(0,0), B=(6,0), C=(3,4);\ndraw(A--B--C--cycle);\ndraw(C--(A+B)/2,linetype(\"2 3\"));\nlabel(\"5\",(A+C)/2,unit((-4,3)));\nlabel(\"3\",B/4,S);\ndraw(\"6\",shift((0,-0.6))*(A--B),Bars(5));\ndraw(rightanglemark(A,(A+B)/2,C));[/asy]"
}

MATH_GEO_HARD = {
    "problem": "A sphere is inscribed inside a hemisphere of radius 2.  What is the volume of this sphere?",
    "level": "Level 4",
    "type": "Geometry",
    "answer":"\\frac{4}{3}\\pi",
    "solution": "[asy]\n\nsize(110); dotfactor=4; pen dps=linewidth(0.7)+fontsize(10); defaultpen(dps);\ndraw(scale(1,.2)*arc((0,0),1,0,180),dashed);\ndraw(scale(1,.2)*arc((0,0),1,180,360));\ndraw(Arc((0,0),1,0,180));\n\ndraw(Circle((0,.5),.5),heavycyan);\ndraw(scale(1,.2)*arc((0,2.5),.5,0,180),dashed+heavycyan);\ndraw(scale(1,.2)*arc((0,2.5),.5,180,360),heavycyan);\n\ndot((0,0)); dot((0,1));\nlabel(\"$B$\",(0,0),SW); label(\"$A$\",(0,1),NE);\n\n[/asy]\n\nLet $A$ be the point on the hemisphere where the top of the hemisphere touches the sphere, and let $B$ be the point on the hemisphere where the base of the hemisphere touches the sphere.  $AB$ is a diameter of the sphere and a radius of the hemisphere.  Thus, the diameter of the sphere is 2, so the radius of the sphere is 1 and the volume of the sphere is $\\frac{4}{3}\\pi (1^3)=\\boxed{\\frac{4}{3}\\pi}$."
}

