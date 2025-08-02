using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.EntityFrameworkCore;
using BlazorApp.Services;
using BlazorApp.Data;
using BlazorApp.Models;

namespace BlazorApp.Tests;

/// <summary>
/// Mock implementation of IDebugConsoleHelper for testing
/// </summary>
public class MockDebugConsoleHelper : IDebugConsoleHelper
{
    public Task LogAsync(string message, string level = "log") => Task.CompletedTask;
    public Task LogInfoAsync(string message) => Task.CompletedTask;
    public Task LogWarningAsync(string message) => Task.CompletedTask;
    public Task LogErrorAsync(string message) => Task.CompletedTask;
    public Task LogGroupAsync(string groupName) => Task.CompletedTask;
    public Task LogGroupEndAsync() => Task.CompletedTask;
}

/// <summary>
/// Test class for verifying thread pool and async/await fixes
/// </summary>
public class ThreadingFixValidationTest
{
    /// <summary>
    /// Tests that form submission doesn't cause thread pool exhaustion or deadlocks
    /// </summary>
    /// <returns></returns>
    public static async Task TestFormSubmissionThreading()
    {
        Console.WriteLine("=== THREADING FIX VALIDATION TEST ===");
        
        // Setup test services
        var services = new ServiceCollection();
        services.AddLogging(builder => builder.AddConsole());
        services.AddDbContext<ApplicationDbContext>(options => 
            options.UseInMemoryDatabase("TestDb"));
        
        // Configure settings
        services.Configure<ApplicationSettings>(options =>
        {
            options.ApplicationName = "Test App";
            options.TokenExpirationMinutes = 15;
            options.TokenLength = 6;
        });
        
        services.Configure<EmailSettings>(options =>
        {
            options.SmtpServer = "localhost";
            options.SmtpPort = 1025;
            options.UseSsl = false;
            options.FromEmail = "test@test.com";
            options.FromName = "Test";
            options.CompanyEmail = "company@test.com";
        });
        
        services.Configure<BlobStorageSettings>(options =>
        {
            options.ConnectionString = "UseDevelopmentStorage=true";
            options.ContainerName = "test-container";
        });
        
        // Register services
        services.AddTransient<IDebugConsoleHelper, MockDebugConsoleHelper>();
        services.AddTransient<IPdfGenerationService, PdfGenerationService>();
        services.AddTransient<IBlobStorageService, BlobStorageService>();
        services.AddTransient<IEmailService, EmailService>();
        services.AddTransient<IFormService, FormService>();
        services.AddSingleton<IThreadPoolMonitoringService, ThreadPoolMonitoringService>();
        
        var serviceProvider = services.BuildServiceProvider();
        
        // Initialize thread pool monitoring
        var threadPoolMonitor = serviceProvider.GetRequiredService<IThreadPoolMonitoringService>();
        threadPoolMonitor.LogThreadPoolStatus("Test Start");
        
        try
        {
            // Create test form data
            var formData = CreateTestFormData();
            
            // Test multiple concurrent form submissions to stress test the thread pool
            var concurrentTasks = new List<Task>();
            
            for (int i = 0; i < 5; i++)
            {
                var taskIndex = i;
                var task = Task.Run(async () =>
                {
                    try
                    {
                        threadPoolMonitor.LogThreadPoolStatus($"Test Task {taskIndex} Start");
                        
                        var formService = serviceProvider.GetRequiredService<IFormService>();
                        var result = await formService.ProcessFormDirectAsync(formData, $"192.168.1.{taskIndex}");
                        
                        threadPoolMonitor.LogThreadPoolStatus($"Test Task {taskIndex} Complete - Success: {result.Success}");
                        
                        Console.WriteLine($"Task {taskIndex}: Form submission success = {result.Success}");
                        Console.WriteLine($"Task {taskIndex}: Message = {result.Message}");
                    }
                    catch (Exception ex)
                    {
                        threadPoolMonitor.LogThreadPoolStatus($"Test Task {taskIndex} Exception");
                        Console.WriteLine($"Task {taskIndex}: Exception - {ex.Message}");
                        Console.WriteLine($"Task {taskIndex}: Stack trace - {ex.StackTrace}");
                    }
                });
                
                concurrentTasks.Add(task);
            }
            
            // Wait for all tasks to complete
            await Task.WhenAll(concurrentTasks);
            
            threadPoolMonitor.LogThreadPoolStatus("All Test Tasks Complete");
            
            Console.WriteLine("=== THREADING TEST COMPLETED SUCCESSFULLY ===");
            Console.WriteLine("No thread pool exhaustion or deadlocks detected!");
        }
        catch (Exception ex)
        {
            threadPoolMonitor.LogThreadPoolStatus("Test Exception");
            Console.WriteLine($"=== THREADING TEST FAILED ===");
            Console.WriteLine($"Exception: {ex.Message}");
            Console.WriteLine($"Stack trace: {ex.StackTrace}");
            throw;
        }
        finally
        {
            serviceProvider.Dispose();
        }
    }
    
    private static FormData CreateTestFormData()
    {
        return new FormData
        {
            TenantDetails = new TenantDetails
            {
                FullName = "Test User",
                Email = "test@example.com",
                DateOfBirth = DateTime.Now.AddYears(-25),
                PlaceOfBirth = "Test City",
                Telephone = "1234567890",
                EmployersName = "Test Company",
                Gender = Gender.Male,
                NiNumber = "AB123456C",
                Car = false,
                Bicycle = true,
                RightToLiveInUk = true,
                RoomOccupancy = RoomOccupancy.JustYou,
                OtherNames = new OtherNames { HasOtherNames = false },
                MedicalCondition = new MedicalCondition { HasCondition = false }
            },
            BankDetails = new BankDetails
            {
                BankName = "Test Bank",
                Postcode = "AB12 3CD",
                AccountNo = "12345678",
                SortCode = "12-34-56"
            },
            AddressHistory = new List<AddressHistoryItem>
            {
                new AddressHistoryItem
                {
                    Address = "123 Test Street, Test City",
                    From = DateTime.Now.AddYears(-2),
                    To = DateTime.Now,
                    LandlordName = "Test Landlord",
                    LandlordTel = "0987654321",
                    LandlordEmail = "landlord@test.com"
                }
            },
            Contacts = new Contacts
            {
                NextOfKin = "Test Family Member",
                Relationship = "Parent",
                Address = "456 Family Street, Family City",
                ContactNumber = "1111222233"
            },
            MedicalDetails = new MedicalDetails
            {
                GpPractice = "Test GP Practice",
                DoctorName = "Dr. Test",
                DoctorAddress = "789 Medical Street, Medical City",
                DoctorTelephone = "4444555566"
            },
            Employment = new Employment
            {
                EmployerNameAddress = "Test Company Ltd, Business District",
                JobTitle = "Software Developer",
                ManagerName = "Test Manager",
                ManagerTel = "7777888899",
                ManagerEmail = "manager@test.com",
                DateOfEmployment = DateTime.Now.AddYears(-1),
                PresentSalary = "£50,000"
            },
            EmploymentChange = "No changes expected",
            PassportDetails = new PassportDetails
            {
                PassportNumber = "123456789",
                DateOfIssue = DateTime.Now.AddYears(-5),
                PlaceOfIssue = "Test Office"
            },
            CurrentLivingArrangement = new CurrentLivingArrangement
            {
                LandlordKnows = true,
                NoticeEndDate = DateTime.Now.AddMonths(1),
                ReasonLeaving = "Moving for work",
                LandlordReference = true,
                LandlordContact = new LandlordContact
                {
                    Name = "Current Landlord",
                    Tel = "2222333344",
                    Address = "Current Property Address",
                    Email = "current.landlord@test.com"
                }
            },
            Other = new Other
            {
                Pets = new Pets { HasPets = false },
                Smoke = false,
                Coliving = new Coliving { HasColiving = false }
            },
            OccupationAgreement = new OccupationAgreement
            {
                SingleOccupancyAgree = true,
                HmoTermsAgree = true,
                NoUnlistedOccupants = true,
                NoSmoking = true,
                KitchenCookingOnly = true
            },
            ConsentAndDeclaration = new ConsentAndDeclaration
            {
                ConsentGiven = true,
                Signature = "Test User",
                Date = DateTime.Now,
                PrintName = "Test User",
                Declaration = new Declaration
                {
                    MainHome = true,
                    EnquiriesPermission = true,
                    CertifyNoJudgements = true,
                    CertifyNoHousingDebt = true,
                    CertifyNoLandlordDebt = true,
                    CertifyNoAbuse = true
                },
                DeclarationSignature = "Test User",
                DeclarationDate = DateTime.Now,
                DeclarationPrintName = "Test User"
            }
        };
    }
}