// ✅ CORRECTED inventory-dashboard.js (no vendor)

document.addEventListener('DOMContentLoaded', function () {
  // DELETE
  const deleteButtons = document.querySelectorAll('.delete-material-btn');
  const deleteModal = new bootstrap.Modal(document.getElementById('deleteMaterialModal'));
  const deleteNameDisplay = document.getElementById('delete-material-name');
  const deleteIdInput = document.getElementById('delete-material-id');

  deleteButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      deleteNameDisplay.textContent = this.getAttribute('data-name');
      deleteIdInput.value = this.getAttribute('data-id');
      deleteModal.show();
    });
  });

  // EDIT
  const editButtons = document.querySelectorAll('.edit-material-btn');
  const editModal = new bootstrap.Modal(document.getElementById('editMaterialModal'));
  
  const e_id = document.getElementById('edit-material-id');
  const e_name = document.getElementById('edit-name');
  const e_quantity = document.getElementById('edit-quantity');
  const e_unit = document.getElementById('edit-unit');
  const e_max_quantity = document.getElementById('edit-max_quantity');
  const e_threshold = document.getElementById('edit-threshold');
  // ❌ NO e_vendor — you don't have this field

  editButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      e_id.value = this.getAttribute('data-id');
      e_name.value = this.getAttribute('data-name');
      e_quantity.value = this.getAttribute('data-quantity');
      e_unit.value = this.getAttribute('data-unit');
      e_max_quantity.value = this.getAttribute('data-max');
      e_threshold.value = this.getAttribute('data-threshold');
      // ✅ That's all — no vendor
      editModal.show();
    });
  });

  // Reset forms on close
  document.getElementById('editMaterialModal').addEventListener('hidden.bs.modal', () => {
    document.getElementById('editMaterialForm').reset();
  });
  document.getElementById('addMaterialModal').addEventListener('hidden.bs.modal', () => {
    document.getElementById('addMaterialForm').reset();
  });
});