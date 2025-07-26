using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;
using BlazorApp.Models;

namespace BlazorApp.Services;

public interface IPdfGenerationService
{
    Task<byte[]> GenerateFormPdfAsync(FormData formData, string submissionId, DateTime submissionTime, string clientIpAddress);
    string GenerateFileName(FormData formData, DateTime submissionTime);
}

public class PdfGenerationService : IPdfGenerationService
{
    private readonly ILogger<PdfGenerationService> _logger;

    public PdfGenerationService(ILogger<PdfGenerationService> logger)
    {
        _logger = logger;
        
        // Initialize QuestPDF with Community License
        QuestPDF.Settings.License = LicenseType.Community;
    }

    public async Task<byte[]> GenerateFormPdfAsync(FormData formData, string submissionId, DateTime submissionTime, string clientIpAddress)
    {
        return await Task.Run(() =>
        {
            try
            {
                // DEBUG: Log PDF generation start (production: remove this section)
                Console.WriteLine("=== PDF GENERATION DEBUG ===");
                Console.WriteLine($"Submission ID: {submissionId}");
                Console.WriteLine($"Submission Time: {submissionTime:yyyy-MM-dd HH:mm:ss} UTC");
                Console.WriteLine($"Client IP: {clientIpAddress}");
                Console.WriteLine($"Tenant Name: {formData.TenantDetails.FullName}");
                Console.WriteLine($"Tenant Email: {formData.TenantDetails.Email}");

                _logger.LogInformation("DEBUG - PDF generation started for submission {SubmissionId}, client IP {ClientIp}",
                    submissionId, clientIpAddress);

                var document = Document.Create(container =>
                {
                    container.Page(page =>
                    {
                        page.Size(PageSizes.A4);
                        page.Margin(2, Unit.Centimetre);
                        page.DefaultTextStyle(x => x.FontSize(10));

                        page.Header()
                            .AlignCenter()
                            .Text("Azure Accommodation Application Form")
                            .FontSize(18)
                            .Bold();

                        page.Content()
                            .PaddingVertical(1, Unit.Centimetre)
                            .Column(column =>
                            {
                                // Document metadata
                                column.Item().Row(row =>
                                {
                                    row.RelativeItem().Text($"Submission ID: {submissionId}").FontSize(8).Italic();
                                    row.RelativeItem().AlignRight().Text($"Generated: {DateTime.UtcNow:yyyy-MM-dd HH:mm} UTC").FontSize(8).Italic();
                                });

                                column.Item().PaddingVertical(5, Unit.Millimetre);

                                // Section 1: Tenant Details
                                AddSection(column, "1. Tenant Details");
                                AddField(column, "Full Name", formData.TenantDetails.FullName);
                                AddField(column, "Date of Birth", formData.TenantDetails.DateOfBirth?.ToString("yyyy-MM-dd") ?? "");
                                AddField(column, "Place of Birth", formData.TenantDetails.PlaceOfBirth);
                                AddField(column, "Email", formData.TenantDetails.Email);
                                AddField(column, "Telephone", formData.TenantDetails.Telephone);
                                AddField(column, "Employer's Name", formData.TenantDetails.EmployersName);
                                AddField(column, "Gender", formData.TenantDetails.Gender?.ToString() ?? "");
                                AddField(column, "NI Number", formData.TenantDetails.NiNumber);
                                AddField(column, "Car", formData.TenantDetails.Car ? "Yes" : "No");
                                AddField(column, "Bicycle", formData.TenantDetails.Bicycle ? "Yes" : "No");
                                AddField(column, "Right to Live in UK", formData.TenantDetails.RightToLiveInUk ? "Yes" : "No");
                                AddField(column, "Room Occupancy", formData.TenantDetails.RoomOccupancy?.ToString() ?? "");

                                if (formData.TenantDetails.OtherNames.HasOtherNames)
                                {
                                    AddField(column, "Other Names", formData.TenantDetails.OtherNames.Details);
                                }

                                if (formData.TenantDetails.MedicalCondition.HasCondition)
                                {
                                    AddField(column, "Medical Condition", formData.TenantDetails.MedicalCondition.Details);
                                }

                                column.Item().PaddingVertical(5, Unit.Millimetre);

                                // Section 2: Bank Details
                                AddSection(column, "2. Bank Details");
                                AddField(column, "Bank Name", formData.BankDetails.BankName);
                                AddField(column, "Postcode", formData.BankDetails.Postcode);
                                AddField(column, "Account No", formData.BankDetails.AccountNo);
                                AddField(column, "Sort Code", formData.BankDetails.SortCode);

                                column.Item().PaddingVertical(5, Unit.Millimetre);

                                // Section 3: Address History
                                AddSection(column, "3. Address History");
                                for (int i = 0; i < formData.AddressHistory.Count; i++)
                                {
                                    var address = formData.AddressHistory[i];
                                    AddField(column, $"Address {i + 1}", address.Address);
                                    AddField(column, "From", address.From?.ToString("yyyy-MM-dd") ?? "");
                                    AddField(column, "To", address.To?.ToString("yyyy-MM-dd") ?? "");
                                    AddField(column, "Landlord Name", address.LandlordName);
                                    AddField(column, "Landlord Tel", address.LandlordTel);
                                    AddField(column, "Landlord Email", address.LandlordEmail);
                                    if (i < formData.AddressHistory.Count - 1)
                                    {
                                        column.Item().PaddingVertical(3, Unit.Millimetre);
                                    }
                                }

                                column.Item().PaddingVertical(5, Unit.Millimetre);

                                // Section 4: Contacts
                                AddSection(column, "4. Contacts");
                                AddField(column, "Next of Kin", formData.Contacts.NextOfKin);
                                AddField(column, "Relationship", formData.Contacts.Relationship);
                                AddField(column, "Address", formData.Contacts.Address);
                                AddField(column, "Contact Number", formData.Contacts.ContactNumber);

                                column.Item().PaddingVertical(5, Unit.Millimetre);

                                // Section 5: Medical Details
                                AddSection(column, "5. Medical Details");
                                AddField(column, "GP Practice", formData.MedicalDetails.GpPractice);
                                AddField(column, "Doctor's Name", formData.MedicalDetails.DoctorName);
                                AddField(column, "Doctor's Address", formData.MedicalDetails.DoctorAddress);
                                AddField(column, "Doctor's Telephone", formData.MedicalDetails.DoctorTelephone);

                                column.Item().PaddingVertical(5, Unit.Millimetre);

                                // Section 6: Employment
                                AddSection(column, "6. Employment");
                                AddField(column, "Employer Name", formData.Employment.EmployerName);
                                AddField(column, "Employer Address", formData.Employment.EmployerAddress);
                                AddField(column, "Job Title", formData.Employment.JobTitle);
                                AddField(column, "Manager's Name", formData.Employment.ManagerName);
                                AddField(column, "Manager's Tel", formData.Employment.ManagerTel);
                                AddField(column, "Manager's Email", formData.Employment.ManagerEmail);
                                AddField(column, "Date of Employment", formData.Employment.DateOfEmployment?.ToString("yyyy-MM-dd") ?? "");
                                AddField(column, "Present Salary", formData.Employment.PresentSalary);

                                column.Item().PaddingVertical(5, Unit.Millimetre);

                                // Section 7: Employment Change
                                AddSection(column, "7. Employment Change");
                                AddField(column, "Are circumstances likely to change?", formData.EmploymentChange);

                                column.Item().PaddingVertical(5, Unit.Millimetre);

                                // Section 8: Passport Details
                                AddSection(column, "8. Passport Details");
                                AddField(column, "Passport Number", formData.PassportDetails.PassportNumber);
                                AddField(column, "Date of Issue", formData.PassportDetails.DateOfIssue?.ToString("yyyy-MM-dd") ?? "");
                                AddField(column, "Place of Issue", formData.PassportDetails.PlaceOfIssue);

                                column.Item().PaddingVertical(5, Unit.Millimetre);

                                // Section 9: Current Living Arrangement
                                AddSection(column, "9. Current Living Arrangement");
                                AddField(column, "Landlord Knows", formData.CurrentLivingArrangement.LandlordKnows ? "Yes" : "No");
                                AddField(column, "Notice End Date", formData.CurrentLivingArrangement.NoticeEndDate?.ToString("yyyy-MM-dd") ?? "");
                                AddField(column, "Reason for Leaving", formData.CurrentLivingArrangement.ReasonLeaving);
                                AddField(column, "Landlord Reference", formData.CurrentLivingArrangement.LandlordReference ? "Yes" : "No");
                                AddField(column, "Landlord Contact Name", formData.CurrentLivingArrangement.LandlordContact.Name);
                                AddField(column, "Landlord Contact Tel", formData.CurrentLivingArrangement.LandlordContact.Tel);
                                AddField(column, "Landlord Contact Address", formData.CurrentLivingArrangement.LandlordContact.Address);
                                AddField(column, "Landlord Contact Email", formData.CurrentLivingArrangement.LandlordContact.Email);

                                column.Item().PaddingVertical(5, Unit.Millimetre);

                                // Section 10: Other
                                AddSection(column, "10. Other Details");
                                if (formData.Other.Pets.HasPets)
                                {
                                    AddField(column, "Pets", formData.Other.Pets.Details);
                                }
                                AddField(column, "Smoke", formData.Other.Smoke ? "Yes" : "No");
                                if (formData.Other.Coliving.HasColiving)
                                {
                                    AddField(column, "Co-living", formData.Other.Coliving.Details);
                                }

                                column.Item().PaddingVertical(5, Unit.Millimetre);

                                // Section 11: Occupation Agreement
                                AddSection(column, "11. Occupation Agreement");
                                AddField(column, "Single Occupancy Agree", formData.OccupationAgreement.SingleOccupancyAgree ? "Yes" : "No");
                                AddField(column, "HMO Terms Agree", formData.OccupationAgreement.HmoTermsAgree ? "Yes" : "No");
                                AddField(column, "No Unlisted Occupants", formData.OccupationAgreement.NoUnlistedOccupants ? "Yes" : "No");
                                AddField(column, "No Smoking", formData.OccupationAgreement.NoSmoking ? "Yes" : "No");
                                AddField(column, "Kitchen Cooking Only", formData.OccupationAgreement.KitchenCookingOnly ? "Yes" : "No");

                                column.Item().PaddingVertical(5, Unit.Millimetre);

                                // Section 12: Consent & Declaration
                                AddSection(column, "12. Consent & Declaration");
                                AddField(column, "Consent Given", formData.ConsentAndDeclaration.ConsentGiven ? "Yes" : "No");
                                AddField(column, "Signature", formData.ConsentAndDeclaration.Signature);
                                AddField(column, "Date", formData.ConsentAndDeclaration.Date?.ToString("yyyy-MM-dd") ?? "");
                                AddField(column, "Print Name", formData.ConsentAndDeclaration.PrintName);

                                // Declaration fields
                                AddField(column, "Main Home", formData.ConsentAndDeclaration.Declaration.MainHome ? "Yes" : "No");
                                AddField(column, "Enquiries Permission", formData.ConsentAndDeclaration.Declaration.EnquiriesPermission ? "Yes" : "No");
                                AddField(column, "No Judgements", formData.ConsentAndDeclaration.Declaration.CertifyNoJudgements ? "Yes" : "No");
                                AddField(column, "No Housing Debt", formData.ConsentAndDeclaration.Declaration.CertifyNoHousingDebt ? "Yes" : "No");
                                AddField(column, "No Landlord Debt", formData.ConsentAndDeclaration.Declaration.CertifyNoLandlordDebt ? "Yes" : "No");
                                AddField(column, "No Abuse", formData.ConsentAndDeclaration.Declaration.CertifyNoAbuse ? "Yes" : "No");

                                AddField(column, "Declaration Signature", formData.ConsentAndDeclaration.DeclarationSignature);
                                AddField(column, "Declaration Date", formData.ConsentAndDeclaration.DeclarationDate?.ToString("yyyy-MM-dd") ?? "");
                                AddField(column, "Declaration Print Name", formData.ConsentAndDeclaration.DeclarationPrintName);

                                column.Item().PaddingVertical(10, Unit.Millimetre);

                                // Audit Trail Section
                                AddSection(column, "Audit Trail");
                                column.Item().BorderColor(Colors.Grey.Medium).BorderLeft(2, Unit.Point).PaddingLeft(10, Unit.Point).Column(auditColumn =>
                                {
                                    AddField(auditColumn, "Form Submitted", submissionTime.ToString("yyyy-MM-dd HH:mm:ss") + " UTC");
                                    AddField(auditColumn, "Client IP Address", clientIpAddress);
                                    AddField(auditColumn, "PDF Generated", DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss") + " UTC");
                                });
                            });

                        page.Footer()
                            .AlignCenter()
                            .Text(x =>
                            {
                                x.Span("Page ");
                                x.CurrentPageNumber();
                                x.Span(" of ");
                                x.TotalPages();
                            });
                    });
                });

                var pdfBytes = document.GeneratePdf();

                // DEBUG: Save PDF locally for debugging (production: remove this section)
                SavePdfLocally(pdfBytes, submissionId, submissionTime);

                // DEBUG: Log PDF generation completion (production: remove this section)
                Console.WriteLine($"=== PDF GENERATED SUCCESSFULLY ===");
                Console.WriteLine($"PDF Size: {pdfBytes.Length} bytes");

                _logger.LogInformation("DEBUG - PDF generated successfully for submission {SubmissionId}, size {PdfSize} bytes",
                    submissionId, pdfBytes.Length);

                return pdfBytes;
            }
            catch (Exception ex)
            {
                // DEBUG: Enhanced error logging (production: keep but remove DEBUG prefix)
                Console.WriteLine($"=== PDF GENERATION FAILED ===");
                Console.WriteLine($"Error: {ex.Message}");
                Console.WriteLine($"Stack trace: {ex.StackTrace}");
                
                _logger.LogError(ex, "Failed to generate PDF for submission {SubmissionId} from IP {ClientIp}", submissionId, clientIpAddress);
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

    private void AddSection(ColumnDescriptor column, string title)
    {
        column.Item().Text(title).FontSize(12).Bold();
        column.Item().PaddingVertical(2, Unit.Millimetre);
    }

    private void AddField(ColumnDescriptor column, string label, string value)
    {
        if (!string.IsNullOrWhiteSpace(value))
        {
            column.Item().Row(row =>
            {
                row.ConstantItem(120).Text($"{label}:").Bold();
                row.RelativeItem().Text(value);
            });
        }
    }

    private string SanitizeFileName(string fileName)
    {
        var invalidChars = Path.GetInvalidFileNameChars();
        var sanitized = new System.Text.StringBuilder();
        
        foreach (char c in fileName)
        {
            if (!invalidChars.Contains(c) && c != ' ')
            {
                sanitized.Append(c);
            }
        }
        
        return sanitized.ToString();
    }

    // DEBUG: Save PDF locally for debugging purposes (production: remove this method)
    private void SavePdfLocally(byte[] pdfBytes, string submissionId, DateTime submissionTime)
    {
        try
        {
            // Get the project root directory (assuming we're running from BlazorApp/bin/Debug/net8.0/)
            var currentDirectory = Directory.GetCurrentDirectory();
            var projectRoot = currentDirectory;
            
            // Navigate up to find the project root if we're in bin directory
            if (currentDirectory.Contains("bin"))
            {
                var binIndex = currentDirectory.IndexOf("bin");
                projectRoot = currentDirectory.Substring(0, binIndex);
            }
            
            // Create debug directory at project root
            var debugDir = Path.Combine(projectRoot, "KitDocuments_Debug");
            Directory.CreateDirectory(debugDir);
            
            // Create filename with submission ID and timestamp
            var timestamp = submissionTime.ToString("yyyyMMdd_HHmmss");
            var fileName = $"{submissionId}_{timestamp}_debug.pdf";
            var filePath = Path.Combine(debugDir, fileName);
            
            // Save the PDF file
            File.WriteAllBytes(filePath, pdfBytes);
            
            Console.WriteLine($"=== PDF SAVED LOCALLY ===");
            Console.WriteLine($"Debug PDF saved to: {filePath}");
            
            _logger.LogInformation("DEBUG - PDF saved locally to: {FilePath}", filePath);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"=== PDF LOCAL SAVE FAILED ===");
            Console.WriteLine($"Error: {ex.Message}");
            
            _logger.LogWarning(ex, "DEBUG - Failed to save PDF locally for submission {SubmissionId}", submissionId);
        }
    }
}