// Smooth animations on page load
document.addEventListener('DOMContentLoaded', function () {
  // DELETE LOGIC
  const deleteButtons = document.querySelectorAll('.delete-btn');
  const deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
  const deleteClientName = document.getElementById('delete-client-name');
  const deleteClientId = document.getElementById('delete-client-id');

  deleteButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const name = this.getAttribute('data-client-name');
      const id = this.getAttribute('data-client-id');
      deleteClientName.textContent = name;
      deleteClientId.value = id;
      deleteModal.show();
    });
  });

  // EDIT/ADD LOGIC
  const editButtons = document.querySelectorAll('.edit-client-btn');
  const modalTitle = document.getElementById('modal-title');
  const modalSubmitBtn = document.getElementById('modal-submit-btn');
  const formClientId = document.getElementById('form-client-id');
  const avatarPreview = document.getElementById('avatar-preview');
  const avatarImg = document.getElementById('avatar-img');

// Reset form when modal closes
document.getElementById('addClientModal').addEventListener('hidden.bs.modal', function () {
  document.getElementById('clientForm').reset();
  formClientId.value = '';
  avatarPreview.classList.remove('show-preview');
  setTimeout(() => {
    avatarPreview.style.display = 'none';
  }, 300);
  modalTitle.textContent = 'Add New Client';
  modalSubmitBtn.textContent = 'Save Client';
});

  // Handle Edit Button Click
  editButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const id = this.getAttribute('data-id');
      const name = this.getAttribute('data-name');
      const email = this.getAttribute('data-email');
      const phone = this.getAttribute('data-phone');
      const company = this.getAttribute('data-company');
      const isActive = this.getAttribute('data-is_active') === 'true';
      const avatarUrl = this.getAttribute('data-avatar-url');

      // Fill form
      formClientId.value = id;
      document.getElementById('form-name').value = name;
      document.getElementById('form-email').value = email;
      document.getElementById('form-phone').value = phone;
      document.getElementById('form-company').value = company;
      document.getElementById('form-is_active').checked = isActive;

// Handle avatar preview
if (avatarUrl) {
  avatarImg.src = avatarUrl;
  avatarPreview.style.display = 'block';
  // Small delay to allow display:block to apply before adding class
  setTimeout(() => {
    avatarPreview.classList.add('show-preview');
  }, 10);
} else {
  avatarPreview.classList.remove('show-preview');
  setTimeout(() => {
    avatarPreview.style.display = 'none';
  }, 300);
}

      // Update modal title & button
      modalTitle.textContent = 'Edit Client';
      modalSubmitBtn.textContent = 'Update Client';
    });
  });
  
  // SEARCH - REMOVED AUTO-SUBMIT TO PREVENT RELOAD
  // Users must press Enter or click the status filter to submit
  const searchInput = document.querySelector('input[name="search"]');
  if (searchInput) {
    searchInput.addEventListener('keypress', function(e) {
      // Only submit when Enter key is pressed
      if (e.key === 'Enter') {
        this.form.submit();
      }
    });
  }
});