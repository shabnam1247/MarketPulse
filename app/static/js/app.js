document.addEventListener(
    "DOMContentLoaded",
    () => {


        const mobileMenu =
            document.getElementById(
                "mobileMenu"
            );


        const sidebar =
            document.getElementById(
                "sidebar"
            );


        const themeToggle =
            document.getElementById(
                "themeToggle"
            );


        // =========================
        // MOBILE MENU
        // =========================

        if (
            mobileMenu &&
            sidebar
        ) {

            mobileMenu.addEventListener(
                "click",
                () => {

                    sidebar.classList.toggle(
                        "open"
                    );

                }
            );

        }


        // =========================
        // DARK MODE
        // =========================

        const savedTheme =
            localStorage.getItem(
                "marketpulse-theme"
            );


        if (
            savedTheme === "dark"
        ) {

            document.body.classList.add(
                "dark"
            );

            updateThemeIcon();

        }


        if (themeToggle) {


            themeToggle.addEventListener(
                "click",
                () => {


                    document.body.classList.toggle(
                        "dark"
                    );


                    const theme =
                        document.body.classList.contains(
                            "dark"
                        )
                            ? "dark"
                            : "light";


                    localStorage.setItem(
                        "marketpulse-theme",
                        theme
                    );


                    updateThemeIcon();


                }
            );


        }


        function updateThemeIcon() {


            if (!themeToggle) {
                return;
            }


            const icon =
                themeToggle.querySelector(
                    "i"
                );


            if (!icon) {
                return;
            }


            if (
                document.body.classList.contains(
                    "dark"
                )
            ) {

                icon.className =
                    "bi bi-sun";

            }

            else {

                icon.className =
                    "bi bi-moon-stars";

            }


        }


        // =========================
        // AUTO REFRESH
        // =========================

        const refreshSeconds =
            window.MARKETPULSE?.refreshSeconds
            || 0;


        if (

            refreshSeconds > 0 &&

            window.location.pathname === "/"

        ) {

            setTimeout(

                () => {

                    window.location.reload();

                },

                refreshSeconds * 1000

            );

        }


    }
);