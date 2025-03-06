document.addEventListener("DOMContentLoaded", function () {
    const categoryField = document.querySelector("#id_category");
    const subcategoryField = document.querySelector("#id_subcategory");
    const subSubcategoryField = document.querySelector("#id_sub_subcategory");

    function updateDropdown(url, field, placeholder) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                field.innerHTML = `<option value="">${placeholder}</option>`;
                data.forEach(item => {
                    field.innerHTML += `<option value="${item.id}">${item.name}</option>`;
                });
            })
            .catch(error => console.error("Error fetching data:", error));
    }

    categoryField.addEventListener("change", function () {
        let categoryId = categoryField.value;
        if (categoryId) {
            updateDropdown(`/products/get-subcategories/${categoryId}/`, subcategoryField, "Select Subcategory");
        } else {
            subcategoryField.innerHTML = '<option value="">Select Subcategory</option>';
            subSubcategoryField.innerHTML = '<option value="">Select Sub-Subcategory</option>';
        }
    });

    subcategoryField.addEventListener("change", function () {
        let subcategoryId = subcategoryField.value;
        if (subcategoryId) {
            updateDropdown(`/products/get-sub-subcategories/${subcategoryId}/`, subSubcategoryField, "Select Sub-Subcategory");
        } else {
            subSubcategoryField.innerHTML = '<option value="">Select Sub-Subcategory</option>';
        }
    });
});
