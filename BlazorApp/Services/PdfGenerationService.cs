using iTextSharp.text;
using iTextSharp.text.pdf;
using BlazorApp.Models;
using System.Text;

namespace BlazorApp.Services;

public interface IPdfGenerationService
{
    Task<byte[]> GenerateFormPdfAsync(FormData formData, string submissionId);
    string GenerateFileName(FormData formData, DateTime submissionTime);
}

public class PdfGenerationService : IPdfGenerationService
{
    private readonly ILogger<PdfGenerationService> _logger;

    public PdfGenerationService(ILogger<PdfGenerationService> logger)
    {
        _logger = logger;
    }

    public async Task<byte[]> GenerateFormPdfAsync(FormData formData, string submissionId)
    {
        return await Task.Run(() =>
        {
            try
            {
                using var memoryStream = new MemoryStream();
                var document = new Document(PageSize.A4, 50, 50, 25, 25);
                var writer = PdfWriter.GetInstance(document, memoryStream);
                
                document.Open();
                
                // Add title
                var titleFont = FontFactory.GetFont(FontFactory.HELVETICA_BOLD, 16, new BaseColor(0, 0, 0));
                var headerFont = FontFactory.GetFont(FontFactory.HELVETICA_BOLD, 12, new BaseColor(0, 0, 0));
                var normalFont = FontFactory.GetFont(FontFactory.HELVETICA, 10, new BaseColor(0, 0, 0));
                var smallFont = FontFactory.GetFont(FontFactory.HELVETICA, 8, new BaseColor(128, 128, 128));
                
                document.Add(new Paragraph("Azure Accommodation Application Form", titleFont));
                document.Add(new Paragraph($"Submission ID: {submissionId}", smallFont));
                document.Add(new Paragraph($"Generated: {DateTime.UtcNow:yyyy-MM-dd HH:mm} UTC", smallFont));
                document.Add(new Paragraph(" ")); // Empty line
                
                // Section 1: Tenant Details
                AddSection(document, "1. Tenant Details", headerFont, normalFont);
                AddField(document, "Full Name", formData.TenantDetails.FullName, normalFont);
                AddField(document, "Date of Birth", formData.TenantDetails.DateOfBirth?.ToString("yyyy-MM-dd") ?? "", normalFont);
                AddField(document, "Place of Birth", formData.TenantDetails.PlaceOfBirth, normalFont);
                AddField(document, "Email", formData.TenantDetails.Email, normalFont);
                AddField(document, "Telephone", formData.TenantDetails.Telephone, normalFont);
                AddField(document, "Employer's Name", formData.TenantDetails.EmployersName, normalFont);
                AddField(document, "Gender", formData.TenantDetails.Gender?.ToString() ?? "", normalFont);
                AddField(document, "NI Number", formData.TenantDetails.NiNumber, normalFont);
                AddField(document, "Car", formData.TenantDetails.Car ? "Yes" : "No", normalFont);
                AddField(document, "Bicycle", formData.TenantDetails.Bicycle ? "Yes" : "No", normalFont);
                AddField(document, "Right to Live in UK", formData.TenantDetails.RightToLiveInUk ? "Yes" : "No", normalFont);
                AddField(document, "Room Occupancy", formData.TenantDetails.RoomOccupancy?.ToString() ?? "", normalFont);
                
                if (formData.TenantDetails.OtherNames.HasOtherNames)
                {
                    AddField(document, "Other Names", formData.TenantDetails.OtherNames.Details, normalFont);
                }
                
                if (formData.TenantDetails.MedicalCondition.HasCondition)
                {
                    AddField(document, "Medical Condition", formData.TenantDetails.MedicalCondition.Details, normalFont);
                }
                
                document.Add(new Paragraph(" "));
                
                // Section 2: Bank Details
                AddSection(document, "2. Bank Details", headerFont, normalFont);
                AddField(document, "Bank Name", formData.BankDetails.BankName, normalFont);
                AddField(document, "Postcode", formData.BankDetails.Postcode, normalFont);
                AddField(document, "Account No", formData.BankDetails.AccountNo, normalFont);
                AddField(document, "Sort Code", formData.BankDetails.SortCode, normalFont);
                
                document.Add(new Paragraph(" "));
                
                // Section 3: Address History
                AddSection(document, "3. Address History", headerFont, normalFont);
                for (int i = 0; i < formData.AddressHistory.Count; i++)
                {
                    var address = formData.AddressHistory[i];
                    AddField(document, $"Address {i + 1}", address.Address, normalFont);
                    AddField(document, "From", address.From?.ToString("yyyy-MM-dd") ?? "", normalFont);
                    AddField(document, "To", address.To?.ToString("yyyy-MM-dd") ?? "", normalFont);
                    AddField(document, "Landlord Name", address.LandlordName, normalFont);
                    AddField(document, "Landlord Tel", address.LandlordTel, normalFont);
                    AddField(document, "Landlord Email", address.LandlordEmail, normalFont);
                    document.Add(new Paragraph(" "));
                }
                
                // Section 4: Contacts
                AddSection(document, "4. Contacts", headerFont, normalFont);
                AddField(document, "Next of Kin", formData.Contacts.NextOfKin, normalFont);
                AddField(document, "Relationship", formData.Contacts.Relationship, normalFont);
                AddField(document, "Address", formData.Contacts.Address, normalFont);
                AddField(document, "Contact Number", formData.Contacts.ContactNumber, normalFont);
                
                document.Add(new Paragraph(" "));
                
                // Section 5: Medical Details
                AddSection(document, "5. Medical Details", headerFont, normalFont);
                AddField(document, "GP Practice", formData.MedicalDetails.GpPractice, normalFont);
                AddField(document, "Doctor's Name", formData.MedicalDetails.DoctorName, normalFont);
                AddField(document, "Doctor's Address", formData.MedicalDetails.DoctorAddress, normalFont);
                AddField(document, "Doctor's Telephone", formData.MedicalDetails.DoctorTelephone, normalFont);
                
                document.Add(new Paragraph(" "));
                
                // Section 6: Employment
                AddSection(document, "6. Employment", headerFont, normalFont);
                AddField(document, "Employer Name", formData.Employment.EmployerName, normalFont);
                AddField(document, "Employer Address", formData.Employment.EmployerAddress, normalFont);
                AddField(document, "Job Title", formData.Employment.JobTitle, normalFont);
                AddField(document, "Manager's Name", formData.Employment.ManagerName, normalFont);
                AddField(document, "Manager's Tel", formData.Employment.ManagerTel, normalFont);
                AddField(document, "Manager's Email", formData.Employment.ManagerEmail, normalFont);
                AddField(document, "Date of Employment", formData.Employment.DateOfEmployment?.ToString("yyyy-MM-dd") ?? "", normalFont);
                AddField(document, "Present Salary", formData.Employment.PresentSalary, normalFont);
                
                document.Add(new Paragraph(" "));
                
                // Section 7: Employment Change
                AddSection(document, "7. Employment Change", headerFont, normalFont);
                AddField(document, "Are circumstances likely to change?", formData.EmploymentChange, normalFont);
                
                document.Add(new Paragraph(" "));
                
                // Section 8: Passport Details
                AddSection(document, "8. Passport Details", headerFont, normalFont);
                AddField(document, "Passport Number", formData.PassportDetails.PassportNumber, normalFont);
                AddField(document, "Date of Issue", formData.PassportDetails.DateOfIssue?.ToString("yyyy-MM-dd") ?? "", normalFont);
                AddField(document, "Place of Issue", formData.PassportDetails.PlaceOfIssue, normalFont);
                
                document.Add(new Paragraph(" "));
                
                // Section 9: Current Living Arrangement
                AddSection(document, "9. Current Living Arrangement", headerFont, normalFont);
                AddField(document, "Landlord Knows", formData.CurrentLivingArrangement.LandlordKnows ? "Yes" : "No", normalFont);
                AddField(document, "Notice End Date", formData.CurrentLivingArrangement.NoticeEndDate?.ToString("yyyy-MM-dd") ?? "", normalFont);
                AddField(document, "Reason for Leaving", formData.CurrentLivingArrangement.ReasonLeaving, normalFont);
                AddField(document, "Landlord Reference", formData.CurrentLivingArrangement.LandlordReference ? "Yes" : "No", normalFont);
                AddField(document, "Landlord Contact Name", formData.CurrentLivingArrangement.LandlordContact.Name, normalFont);
                AddField(document, "Landlord Contact Tel", formData.CurrentLivingArrangement.LandlordContact.Tel, normalFont);
                AddField(document, "Landlord Contact Address", formData.CurrentLivingArrangement.LandlordContact.Address, normalFont);
                AddField(document, "Landlord Contact Email", formData.CurrentLivingArrangement.LandlordContact.Email, normalFont);
                
                document.Add(new Paragraph(" "));
                
                // Section 10: Other
                AddSection(document, "10. Other Details", headerFont, normalFont);
                if (formData.Other.Pets.HasPets)
                {
                    AddField(document, "Pets", formData.Other.Pets.Details, normalFont);
                }
                AddField(document, "Smoke", formData.Other.Smoke ? "Yes" : "No", normalFont);
                if (formData.Other.Coliving.HasColiving)
                {
                    AddField(document, "Co-living", formData.Other.Coliving.Details, normalFont);
                }
                
                document.Add(new Paragraph(" "));
                
                // Section 11: Occupation Agreement
                AddSection(document, "11. Occupation Agreement", headerFont, normalFont);
                AddField(document, "Single Occupancy Agree", formData.OccupationAgreement.SingleOccupancyAgree ? "Yes" : "No", normalFont);
                AddField(document, "HMO Terms Agree", formData.OccupationAgreement.HmoTermsAgree ? "Yes" : "No", normalFont);
                AddField(document, "No Unlisted Occupants", formData.OccupationAgreement.NoUnlistedOccupants ? "Yes" : "No", normalFont);
                AddField(document, "No Smoking", formData.OccupationAgreement.NoSmoking ? "Yes" : "No", normalFont);
                AddField(document, "Kitchen Cooking Only", formData.OccupationAgreement.KitchenCookingOnly ? "Yes" : "No", normalFont);
                
                document.Add(new Paragraph(" "));
                
                // Section 12: Consent & Declaration
                AddSection(document, "12. Consent & Declaration", headerFont, normalFont);
                AddField(document, "Consent Given", formData.ConsentAndDeclaration.ConsentGiven ? "Yes" : "No", normalFont);
                AddField(document, "Signature", formData.ConsentAndDeclaration.Signature, normalFont);
                AddField(document, "Date", formData.ConsentAndDeclaration.Date?.ToString("yyyy-MM-dd") ?? "", normalFont);
                AddField(document, "Print Name", formData.ConsentAndDeclaration.PrintName, normalFont);
                
                // Declaration fields
                AddField(document, "Main Home", formData.ConsentAndDeclaration.Declaration.MainHome ? "Yes" : "No", normalFont);
                AddField(document, "Enquiries Permission", formData.ConsentAndDeclaration.Declaration.EnquiriesPermission ? "Yes" : "No", normalFont);
                AddField(document, "No Judgements", formData.ConsentAndDeclaration.Declaration.CertifyNoJudgements ? "Yes" : "No", normalFont);
                AddField(document, "No Housing Debt", formData.ConsentAndDeclaration.Declaration.CertifyNoHousingDebt ? "Yes" : "No", normalFont);
                AddField(document, "No Landlord Debt", formData.ConsentAndDeclaration.Declaration.CertifyNoLandlordDebt ? "Yes" : "No", normalFont);
                AddField(document, "No Abuse", formData.ConsentAndDeclaration.Declaration.CertifyNoAbuse ? "Yes" : "No", normalFont);
                
                AddField(document, "Declaration Signature", formData.ConsentAndDeclaration.DeclarationSignature, normalFont);
                AddField(document, "Declaration Date", formData.ConsentAndDeclaration.DeclarationDate?.ToString("yyyy-MM-dd") ?? "", normalFont);
                AddField(document, "Declaration Print Name", formData.ConsentAndDeclaration.DeclarationPrintName, normalFont);
                
                document.Close();
                
                return memoryStream.ToArray();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to generate PDF for submission {SubmissionId}", submissionId);
                throw;
            }
        });
    }

    public string GenerateFileName(FormData formData, DateTime submissionTime)
    {
        var firstName = SanitizeFileName(formData.TenantDetails.FullName.Split(' ').FirstOrDefault() ?? "Unknown");
        var lastName = SanitizeFileName(formData.TenantDetails.FullName.Split(' ').LastOrDefault() ?? "User");
        var timestamp = submissionTime.ToString("ddMMyyyyHHmm");
        
        return $"{firstName}_{lastName}_Application_Form_{timestamp}.pdf";
    }

    private void AddSection(Document document, string title, Font headerFont, Font normalFont)
    {
        document.Add(new Paragraph(title, headerFont));
        document.Add(new Paragraph(" "));
    }

    private void AddField(Document document, string label, string value, Font font)
    {
        if (!string.IsNullOrWhiteSpace(value))
        {
            document.Add(new Paragraph($"{label}: {value}", font));
        }
    }

    private string SanitizeFileName(string fileName)
    {
        var invalidChars = Path.GetInvalidFileNameChars();
        var sanitized = new StringBuilder();
        
        foreach (char c in fileName)
        {
            if (!invalidChars.Contains(c) && c != ' ')
            {
                sanitized.Append(c);
            }
        }
        
        return sanitized.ToString();
    }
}