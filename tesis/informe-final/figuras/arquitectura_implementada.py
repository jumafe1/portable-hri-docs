#!/usr/bin/env python3
"""Genera figuras/arquitectura_implementada.pdf (figura de la arquitectura implementada).

Uso:  python3 arquitectura_implementada.py
Requiere Matplotlib. Los recuadros con borde discontinuo indican extensiones previstas.
"""
from pathlib import Path

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

W, H = 792, 533  # unidades de dibujo (la figura mide 7,2 x 4,85 pulgadas)
EDGE, DARK, LIGHT = "#6b6b6b", "#333333", "#efefef"

fig = plt.figure(figsize=(7.2, 4.85))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis("off")


def box(x0, y0, x1, y1, title, subtitle, face="white", text="#111111", dashed=False):
    ax.add_patch(FancyBboxPatch(
        (x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=5",
        facecolor=face, edgecolor=DARK if face == DARK else EDGE, linewidth=1.1,
        linestyle=(0, (3, 2)) if dashed else "solid"))
    middle = (x0 + x1) / 2
    ax.text(middle, y0 + (y1 - y0) * 0.32, title, ha="center", va="center",
            fontsize=10.2, fontweight="bold", color=text)
    ax.text(middle, y0 + (y1 - y0) * 0.70, subtitle, ha="center", va="center",
            fontsize=9.0, color=text)


def arrow(x, y0, y1):
    ax.annotate("", xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle="-|>", color="#555555", linewidth=1.2,
                                shrinkA=0, shrinkB=0, mutation_scale=11))


box(27, 10, 765, 75, "Aplicación HRI en Python · Orquestación con YASMIN",
    "Pausa por voz, adquisición de una persona, seguimiento y parada", face=DARK, text="white")
box(27, 106, 765, 182, "Contratos comunes sobre ROS 2",
    "DetectPeople   ·   MoveVelocity   ·   TranscribeSpeech   ·   Speak", face=LIGHT)
box(27, 212, 765, 288, "Selección por perfil y gestión con Capabilities2",
    "El perfil especifica los proveedores, los recursos ROS y los parámetros del robot.", face=LIGHT)
arrow(396, 75, 106)
arrow(396, 182, 212)

columns = (
    (22, 256, "Proveedores de NAO", "YOLO, Vosk y NAOqi", "NAO", "Aplicación completa probada", False),
    (279, 513, "Perfil del MentorPi", "YOLO y base móvil, sin voz", "Hiwonder MentorPi",
     "Seguimiento probado", False),
    (537, 771, "Otro adaptador", "Capacidades compatibles", "Otra plataforma", "Extensión prevista", True),
)
centers = [(x0 + x1) / 2 for x0, x1, *_ in columns]
ax.plot([396, 396], [288, 315], color="#555555", linewidth=1.2)
ax.plot([centers[0], centers[-1]], [315, 315], color="#555555", linewidth=1.2)
for (x0, x1, provider, detail, robot, state, dashed), center in zip(columns, centers):
    arrow(center, 315, 338)
    box(x0, 338, x1, 408, provider, detail, dashed=dashed)
    arrow(center, 408, 447)
    box(x0, 447, x1, 517, robot, state, dashed=dashed)

fig.savefig(Path(__file__).with_suffix(".pdf"))
