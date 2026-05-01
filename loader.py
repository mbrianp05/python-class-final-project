import customtkinter as ctk
import tksvg


def load_fonts_files():
    ctk.FontManager.load_font("fonts/InterVariable.ttf")


def get_fonts():
    return {
        "title": ctk.CTkFont(family="Inter Variable", size=25),
        "bold": ctk.CTkFont(family="Inter Variable", size=15, weight="bold"),
    }


def get_icons():
    return {
        "gear": tksvg.SvgImage(file="./icons/gear.svg", scaletoheight=26),
        "gear_darker": tksvg.SvgImage(file="./icons/gear_darker.svg", scaletoheight=26),
    }
