import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.lines import Line2D

PTABLE = pd.read_csv("Periodic Table of Elements.csv")


def find_electrons(element_symbol):
    element_data = PTABLE[PTABLE["Symbol"] == element_symbol.capitalize()]
    if not element_data.empty:
        electrons = element_data["NumberofElectrons"].iloc[0]
        return electrons
    else:
        return None


# ELECTRON CONFIGURATION!!!
def electron_configuration(num_electrons):
    orbitals = [
        "1s",
        "2s",
        "2p",
        "3s",
        "3p",
        "4s",
        "3d",
        "4p",
        "5s",
        "4d",
        "5p",
        "6s",
        "4f",
        "5d",
        "6p",
        "7s",
        "5f",
        "6d",
        "7p",
    ]

    electron_count = 0
    orbital_index = 0
    electron_contents = {}

    while electron_count < num_electrons and orbital_index < len(orbitals):
        orbital = orbitals[orbital_index]
        if orbital.endswith("s"):
            max_electrons = 2
        elif orbital.endswith("p"):
            max_electrons = 6
        elif orbital.endswith("d"):
            max_electrons = 10
        elif orbital.endswith("f"):
            max_electrons = 14
        electrons_added = min(num_electrons - electron_count, max_electrons)

        # fill the orbital with electrons and their spin direction
        for i in range(electrons_added):
            if orbital not in electron_contents:
                electron_contents[orbital] = {"up": 0, "down": 0}
            if electron_contents[orbital]["up"] < max_electrons // 2:
                electron_contents[orbital]["up"] += 1
            else:
                electron_contents[orbital]["down"] += 1
            electron_count += 1

        orbital_index += 1

    return electron_contents


def compute_quantum_numbers(electron_configuration_dict):
    quantum_numbers = {}
    for orbital, electrons in electron_configuration_dict.items():
        n = int(re.findall(r"\d+", orbital)[0])
        l = 0 if orbital.endswith("s") else n - 1
        m_values = list(range(-l, l + 1))
        m_index = 0

        for spin, count in electrons.items():
            for _ in range(count):
                m = m_values[m_index % len(m_values)]
                m_index += 1
                s = 1 / 2 if spin == "up" else -1 / 2
                if orbital not in quantum_numbers:
                    quantum_numbers[orbital] = []
                quantum_numbers[orbital].append({"n": n, "l": l, "m": m, "s": s})
    return quantum_numbers


def plot_electrons(quantum_numbers):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    colors = {"spin_up": "b", "spin_down": "r"}
    plotted_point_counts = {}

    for orbital, electrons in quantum_numbers.items():
        for electron in electrons:
            n = electron["n"]
            l = electron["l"]
            m = electron["m"]
            s = electron["s"]

            x = n
            y = l
            z = l + m

            point = (x, y, z)
            if point in plotted_point_counts:
                plotted_point_counts[point] += 1
            else:
                plotted_point_counts[point] = 1

            ax.scatter(
                x,
                y,
                z,
                c=colors["spin_up"] if s == 0.5 else colors["spin_down"],
                marker="o",
                label=f"({x}, {y}, {z})",
                s=100,
            )

    for point, count in plotted_point_counts.items():
        x, y, z = point
        ax.text(
            x,
            y,
            z,
            f"({x}, {y}, {z})\nCount: {count}",
            color="black",
            fontsize=8,
            ha="center",
            va="center",
        )

    ax.set_xlabel("Principal Quantum Number (n)")
    ax.set_ylabel("Azimuthal Quantum Number (l)")
    ax.set_zlabel("Magnetic Quantum Number (m)")

    ax.set_box_aspect([1, 1, 1])

    custom_lines = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="b",
            markersize=10,
            label="Spin Up",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="r",
            markersize=10,
            label="Spin Down",
        ),
    ]
    ax.legend(handles=custom_lines, loc="upper right")

    max_n = max(
        electron["n"]
        for electrons in quantum_numbers.values()
        for electron in electrons
    )
    max_l = max(
        electron["l"]
        for electrons in quantum_numbers.values()
        for electron in electrons
    )
    max_m = max(
        abs(electron["m"])
        for electrons in quantum_numbers.values()
        for electron in electrons
    )
    ax.set_xlim(0, max_n + 1)
    ax.set_ylim(-1, max_l + 1)
    ax.set_zlim(-max_l - max_m - 1, max_l + max_m + 1)

    st.pyplot(fig)


def convert_to_latex(configuration):
    latex_string = r"\begin{align*}"

    for orbital, spins in configuration.items():
        latex_string += rf"{orbital}: & \quad "
        if spins["up"] > 0:
            latex_string += rf"{spins['up']}\uparrow"
        if spins["down"] > 0:
            if spins["up"] > 0:
                latex_string += " \\quad "
            latex_string += rf"{spins['down']}\downarrow"
        latex_string += r"\\"

    latex_string += r"\end{align*}"
    return latex_string


def convert_to_standard_notation(configuration):
    notation = ""
    for orbital, spins in configuration.items():
        if spins["up"] > 0:
            notation += f"{orbital}^{spins['up']}"
        if spins["down"] > 0:
            notation += f"{orbital}^{spins['down']}"

    return notation


def create_quantum_numbers_table(quantum_numbers):
    data = []
    columns = ["Orbital", "Electron", "n", "l", "m", "s"]

    for orbital, electrons in quantum_numbers.items():
        for i, electron in enumerate(electrons, 1):
            n = electron["n"]
            l = electron["l"]
            m = electron["m"]
            s = electron["s"]
            data.append([orbital, i, n, l, m, s])

    df = pd.DataFrame(data, columns=columns)
    return df


st.title("quantum-numbers-of-electons 👨‍🔬")
st.image("Science-cuate.png")
st.divider()

st.write("Enter the symbol of the element:")
element = st.text_input("Element Symbol")

if element:
    num_electrons = find_electrons(element)

    if num_electrons is not None:
        st.write(f"Number of electrons: {num_electrons}")
        configuration = electron_configuration(num_electrons)
        quantum_numbers = compute_quantum_numbers(configuration)
        print(configuration)
        st.header("Orbital Notation")
        st.latex(convert_to_latex(configuration))
        st.header("Standard Notation")
        st.latex(convert_to_standard_notation(configuration))
        st.header(f"Quantum Numbers for Each Electron in {element}")
        quantum_numbers_df = create_quantum_numbers_table(quantum_numbers)
        st.dataframe(quantum_numbers_df)
        st.header("Wicked Cool Graph of All Electron Quantum Numbers")
        st.write("In the form (n,l,m)")
        print(quantum_numbers)
        plot_electrons(quantum_numbers)
        st.header("Quantum Number Definitions")
    else:
        st.write("That's not an element, doofus")
