using System.ComponentModel.DataAnnotations;
using BlazorApp.Models;
using BlazorApp.Controllers;
using BlazorApp.Services;
using BlazorApp.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Moq;
using System.Text.Json;

namespace Tests;

/// <summary>
/// Test class to verify enhanced request metadata capture functionality
/// This test ensures that all request metadata is properly captured and stored
/// </summary>
public class RequestMetadataCaptureTest
{
    public static async Task TestRequestMetadataCapture()
    {
        Console.WriteLine("=== REQUEST METADATA CAPTURE TEST ===");
        Console.WriteLine("Testing enhanced request metadata capture functionality...");

        await TestRequestMetadataModel();
        await TestRequestMetadataExtraction();
        await TestMetadataJsonSerialization();

        Console.WriteLine("✅ All request metadata capture tests passed!");
    }

    /// <summary>
    /// Test that RequestMetadata model captures all required fields
    /// </summary>
    private static async Task TestRequestMetadataModel()
    {
        Console.WriteLine("Testing RequestMetadata model...");

        var metadata = new RequestMetadata
        {
            IpAddress = "203.0.113.195",
            UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            Referrer = "https://example.com/form",
            AcceptLanguage = "en-US,en;q=0.9",
            Origin = "https://example.com",
            XForwardedFor = "203.0.113.195, 70.41.3.18",
            XRealIp = "203.0.113.195",
            ContentType = "application/json",
            ContentLength = 1024,
            RequestTimestamp = DateTime.UtcNow,
            Host = "example.com",
            Protocol = "HTTP/1.1",
            Method = "POST",
            Path = "/api/form/submit-direct",
            QueryString = "?test=1"
        };

        metadata.SecurityHeaders["CF-RAY"] = "72a1b2c3d4e5f6g7-SJC";
        metadata.SecurityHeaders["X-Amzn-Trace-Id"] = "Root=1-61f5a2b4-3456789012345678";

        // Verify all fields are properly set
        if (metadata.IpAddress != "203.0.113.195") throw new Exception("IP address not captured correctly");
        if (!metadata.UserAgent.Contains("Mozilla")) throw new Exception("User-Agent not captured correctly");
        if (metadata.Referrer != "https://example.com/form") throw new Exception("Referrer not captured correctly");
        if (metadata.AcceptLanguage != "en-US,en;q=0.9") throw new Exception("Accept-Language not captured correctly");
        if (metadata.Origin != "https://example.com") throw new Exception("Origin not captured correctly");
        if (metadata.XForwardedFor != "203.0.113.195, 70.41.3.18") throw new Exception("X-Forwarded-For not captured correctly");
        if (metadata.XRealIp != "203.0.113.195") throw new Exception("X-Real-IP not captured correctly");
        if (metadata.ContentType != "application/json") throw new Exception("Content-Type not captured correctly");
        if (metadata.ContentLength != 1024) throw new Exception("Content-Length not captured correctly");
        if (metadata.Host != "example.com") throw new Exception("Host not captured correctly");
        if (metadata.Protocol != "HTTP/1.1") throw new Exception("Protocol not captured correctly");
        if (metadata.Method != "POST") throw new Exception("Method not captured correctly");
        if (metadata.Path != "/api/form/submit-direct") throw new Exception("Path not captured correctly");
        if (metadata.QueryString != "?test=1") throw new Exception("QueryString not captured correctly");
        if (!metadata.SecurityHeaders.ContainsKey("CF-RAY")) throw new Exception("Security headers not captured correctly");
        if (metadata.SecurityHeaders["CF-RAY"] != "72a1b2c3d4e5f6g7-SJC") throw new Exception("CF-RAY header not captured correctly");

        Console.WriteLine("✅ RequestMetadata model test passed");
    }

    /// <summary>
    /// Test request metadata extraction logic
    /// </summary>
    private static async Task TestRequestMetadataExtraction()
    {
        Console.WriteLine("Testing request metadata extraction...");

        // Create mock HTTP context and request
        var httpContext = new DefaultHttpContext();
        var request = httpContext.Request;
        
        // Set up request properties
        request.Method = "POST";
        request.Path = "/api/form/submit-direct";
        request.QueryString = new QueryString("?test=metadata");
        request.Protocol = "HTTP/1.1";
        request.Host = new HostString("localhost:5000");
        request.ContentType = "application/json";
        request.ContentLength = 2048;

        // Add headers
        request.Headers["User-Agent"] = "Test-Agent/1.0";
        request.Headers["Referer"] = "https://localhost:5000/form";
        request.Headers["Accept-Language"] = "en-US,en;q=0.9,fr;q=0.8";
        request.Headers["Origin"] = "https://localhost:5000";
        request.Headers["X-Forwarded-For"] = "192.168.1.100, 10.0.0.1";
        request.Headers["X-Real-IP"] = "192.168.1.100";
        request.Headers["CF-RAY"] = "test-ray-id-12345";
        request.Headers["X-Amzn-Trace-Id"] = "Root=test-trace-id";

        // Set up connection (for IP address)
        httpContext.Connection.RemoteIpAddress = System.Net.IPAddress.Parse("127.0.0.1");

        // Create a controller instance with mocked dependencies
        var logger = new Mock<ILogger<FormController>>();
        var formService = new Mock<IFormService>();
        
        var controller = new FormController(formService.Object, logger.Object)
        {
            ControllerContext = new ControllerContext()
            {
                HttpContext = httpContext
            }
        };

        // Use reflection to call the private CaptureRequestMetadata method
        var method = typeof(FormController).GetMethod("CaptureRequestMetadata", 
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        
        if (method == null)
        {
            throw new Exception("CaptureRequestMetadata method not found");
        }

        var result = method.Invoke(controller, null);
        if (result == null)
        {
            throw new Exception("CaptureRequestMetadata returned null");
        }
        
        var metadata = (RequestMetadata)result;

        // Verify extracted metadata
        if (metadata.IpAddress != "192.168.1.100") throw new Exception($"Expected IP '192.168.1.100', got '{metadata.IpAddress}'");
        if (metadata.UserAgent != "Test-Agent/1.0") throw new Exception($"Expected User-Agent 'Test-Agent/1.0', got '{metadata.UserAgent}'");
        if (metadata.Referrer != "https://localhost:5000/form") throw new Exception($"Expected Referrer 'https://localhost:5000/form', got '{metadata.Referrer}'");
        if (metadata.AcceptLanguage != "en-US,en;q=0.9,fr;q=0.8") throw new Exception($"Expected Accept-Language 'en-US,en;q=0.9,fr;q=0.8', got '{metadata.AcceptLanguage}'");
        if (metadata.Origin != "https://localhost:5000") throw new Exception($"Expected Origin 'https://localhost:5000', got '{metadata.Origin}'");
        if (metadata.XForwardedFor != "192.168.1.100, 10.0.0.1") throw new Exception($"Expected X-Forwarded-For '192.168.1.100, 10.0.0.1', got '{metadata.XForwardedFor}'");
        if (metadata.XRealIp != "192.168.1.100") throw new Exception($"Expected X-Real-IP '192.168.1.100', got '{metadata.XRealIp}'");
        if (metadata.ContentType != "application/json") throw new Exception($"Expected Content-Type 'application/json', got '{metadata.ContentType}'");
        if (metadata.ContentLength != 2048) throw new Exception($"Expected Content-Length 2048, got {metadata.ContentLength}");
        if (metadata.Host != "localhost:5000") throw new Exception($"Expected Host 'localhost:5000', got '{metadata.Host}'");
        if (metadata.Protocol != "HTTP/1.1") throw new Exception($"Expected Protocol 'HTTP/1.1', got '{metadata.Protocol}'");
        if (metadata.Method != "POST") throw new Exception($"Expected Method 'POST', got '{metadata.Method}'");
        if (metadata.Path != "/api/form/submit-direct") throw new Exception($"Expected Path '/api/form/submit-direct', got '{metadata.Path}'");
        if (metadata.QueryString != "?test=metadata") throw new Exception($"Expected QueryString '?test=metadata', got '{metadata.QueryString}'");
        
        // Verify security headers
        if (!metadata.SecurityHeaders.ContainsKey("CF-RAY")) throw new Exception("CF-RAY header not captured");
        if (metadata.SecurityHeaders["CF-RAY"] != "test-ray-id-12345") throw new Exception($"Expected CF-RAY 'test-ray-id-12345', got '{metadata.SecurityHeaders["CF-RAY"]}'");
        if (!metadata.SecurityHeaders.ContainsKey("X-Amzn-Trace-Id")) throw new Exception("X-Amzn-Trace-Id header not captured");
        if (metadata.SecurityHeaders["X-Amzn-Trace-Id"] != "Root=test-trace-id") throw new Exception($"Expected X-Amzn-Trace-Id 'Root=test-trace-id', got '{metadata.SecurityHeaders["X-Amzn-Trace-Id"]}'");

        Console.WriteLine("✅ Request metadata extraction test passed");
    }

    /// <summary>
    /// Test metadata JSON serialization and database storage
    /// </summary>
    private static async Task TestMetadataJsonSerialization()
    {
        Console.WriteLine("Testing metadata JSON serialization...");

        var metadata = new RequestMetadata
        {
            IpAddress = "203.0.113.195",
            UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            Referrer = "https://example.com/form",
            AcceptLanguage = "en-US,en;q=0.9",
            Origin = "https://example.com",
            XForwardedFor = "203.0.113.195, 70.41.3.18",
            XRealIp = "203.0.113.195",
            ContentType = "application/json",
            ContentLength = 1024,
            RequestTimestamp = new DateTime(2024, 1, 15, 10, 30, 0, DateTimeKind.Utc),
            Host = "example.com",
            Protocol = "HTTP/1.1",
            Method = "POST",
            Path = "/api/form/submit-direct",
            QueryString = "?test=1"
        };

        metadata.SecurityHeaders["CF-RAY"] = "72a1b2c3d4e5f6g7-SJC";
        metadata.SecurityHeaders["X-Amzn-Trace-Id"] = "Root=1-61f5a2b4-3456789012345678";

        // Serialize to JSON
        var json = JsonSerializer.Serialize(metadata, new JsonSerializerOptions { WriteIndented = true });
        
        if (string.IsNullOrEmpty(json)) throw new Exception("JSON serialization failed");
        if (!json.Contains("203.0.113.195")) throw new Exception("IP address not in JSON");
        if (!json.Contains("Mozilla/5.0")) throw new Exception("User-Agent not in JSON");
        if (!json.Contains("CF-RAY")) throw new Exception("Security headers not in JSON");
        if (!json.Contains("72a1b2c3d4e5f6g7-SJC")) throw new Exception("CF-RAY value not in JSON");

        // Deserialize back from JSON
        var deserializedMetadata = JsonSerializer.Deserialize<RequestMetadata>(json);
        
        if (deserializedMetadata == null) throw new Exception("JSON deserialization failed");
        if (deserializedMetadata.IpAddress != metadata.IpAddress) throw new Exception("IP address not preserved after serialization");
        if (deserializedMetadata.UserAgent != metadata.UserAgent) throw new Exception("User-Agent not preserved after serialization");
        if (deserializedMetadata.SecurityHeaders.Count != metadata.SecurityHeaders.Count) throw new Exception("Security headers count not preserved");
        if (!deserializedMetadata.SecurityHeaders.ContainsKey("CF-RAY")) throw new Exception("CF-RAY header not preserved");
        if (deserializedMetadata.SecurityHeaders["CF-RAY"] != "72a1b2c3d4e5f6g7-SJC") throw new Exception("CF-RAY value not preserved");

        // Test that JSON fits within database field length constraints (4000 chars)
        if (json.Length > 4000) throw new Exception($"Serialized JSON too long for database field: {json.Length} characters");

        Console.WriteLine("✅ Metadata JSON serialization test passed");
    }
}