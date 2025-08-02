using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BlazorApp.Migrations
{
    /// <inheritdoc />
    public partial class InitialCreate : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "FormSubmissions",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    SubmissionId = table.Column<string>(type: "TEXT", maxLength: 50, nullable: false),
                    FormDataJson = table.Column<string>(type: "TEXT", nullable: false),
                    SubmittedAt = table.Column<DateTime>(type: "TEXT", nullable: false),
                    UserEmail = table.Column<string>(type: "TEXT", maxLength: 320, nullable: false),
                    PdfFileName = table.Column<string>(type: "TEXT", maxLength: 500, nullable: false),
                    BlobStorageUrl = table.Column<string>(type: "TEXT", maxLength: 2000, nullable: false),
                    ClientIpAddress = table.Column<string>(type: "TEXT", nullable: false),
                    Status = table.Column<int>(type: "INTEGER", nullable: false),
                    EmailVerified = table.Column<bool>(type: "INTEGER", nullable: false),
                    EmailVerificationToken = table.Column<string>(type: "TEXT", maxLength: 10, nullable: true),
                    EmailVerificationSent = table.Column<DateTime>(type: "TEXT", nullable: true),
                    EmailVerificationExpires = table.Column<DateTime>(type: "TEXT", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_FormSubmissions", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "FormSubmissionLogs",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    FormSubmissionId = table.Column<int>(type: "INTEGER", nullable: false),
                    Action = table.Column<string>(type: "TEXT", maxLength: 100, nullable: false),
                    Details = table.Column<string>(type: "TEXT", maxLength: 2000, nullable: true),
                    Timestamp = table.Column<DateTime>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_FormSubmissionLogs", x => x.Id);
                    table.ForeignKey(
                        name: "FK_FormSubmissionLogs_FormSubmissions_FormSubmissionId",
                        column: x => x.FormSubmissionId,
                        principalTable: "FormSubmissions",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_FormSubmissionLogs_FormSubmissionId",
                table: "FormSubmissionLogs",
                column: "FormSubmissionId");

            migrationBuilder.CreateIndex(
                name: "IX_FormSubmissionLogs_Timestamp",
                table: "FormSubmissionLogs",
                column: "Timestamp");

            migrationBuilder.CreateIndex(
                name: "IX_FormSubmissions_Status",
                table: "FormSubmissions",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_FormSubmissions_SubmissionId",
                table: "FormSubmissions",
                column: "SubmissionId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_FormSubmissions_SubmittedAt",
                table: "FormSubmissions",
                column: "SubmittedAt");

            migrationBuilder.CreateIndex(
                name: "IX_FormSubmissions_UserEmail",
                table: "FormSubmissions",
                column: "UserEmail");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "FormSubmissionLogs");

            migrationBuilder.DropTable(
                name: "FormSubmissions");
        }
    }
}
