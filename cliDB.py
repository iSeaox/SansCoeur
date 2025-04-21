import argparse
import os
import sys
import logging
import sqlite3
from werkzeug.security import generate_password_hash
import string
import random
import dbManager

# Logging configuration
logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s]<%(name)s> %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("user_management")

def add_user(args, db):
    # Check if the user already exists
    existing_user = db.getUserByName(args.username)
    if existing_user:
        logger.error(f"The user '{args.username}' already exists in the database.")
        return 1

    # Determine the password
    password = args.password
    if not password:
        password = args.username[0]
        logger.info(f"Temporary password generated: {password}")
        print(f"Temporary password generated: {password}")

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Determine if the user must change their password on first login
    should_update_password = 0 if args.no_force_change else 1

    # Add the user
    try:
        db.insertUser(args.username, hashed_password, should_update_password)
        logger.info(f"User '{args.username}' added successfully.")
        print(f"User '{args.username}' added successfully.")
        if should_update_password:
            print("The user will need to change their password on first login.")
        return 0
    except Exception as e:
        logger.error(f"Error adding the user: {e}")
        return 1

def update_password(args, db):
    # Check if the user exists
    existing_user = db.getUserByName(args.username)
    if not existing_user:
        logger.error(f"The user '{args.username}' does not exist in the database.")
        return 1

    # Hash the new password
    hashed_password = generate_password_hash(args.password)

    try:
        # Update the user's password
        db.updateUserPassword(args.username, hashed_password)
        logger.info(f"Password for user '{args.username}' updated successfully.")
        print(f"Password for user '{args.username}' updated successfully.")
        return 0
    except Exception as e:
        logger.error(f"Error updating the password: {e}")
        return 1

def update_password_flag(args, db):
    # Check if the user exists
    existing_user = db.getUserByName(args.username)
    if not existing_user:
        logger.error(f"The user '{args.username}' does not exist in the database.")
        return 1

    # Convert flag to integer value
    should_update_password = 1 if args.require_change else 0

    try:
        # Update the user's password change flag
        db.updateUserPasswordFlag(args.username, should_update_password)
        status = "required" if should_update_password else "not required"
        logger.info(f"Password change on next login for user '{args.username}' is now {status}.")
        print(f"Password change on next login for user '{args.username}' is now {status}.")
        return 0
    except Exception as e:
        logger.error(f"Error updating the password change flag: {e}")
        return 1

def delete_user(args, db):
    """Delete a user from the database"""
    # Check if the user exists
    existing_user = db.getUserByName(args.username)
    if not existing_user:
        logger.error(f"The user '{args.username}' does not exist in the database.")
        return 1

    try:
        # Delete the user
        db.deleteUser(args.username)
        logger.info(f"User '{args.username}' deleted successfully.")
        print(f"User '{args.username}' deleted successfully.")
        return 0
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return 1

def list_users(args, db):
    """List all users in the database in a nicely formatted table"""
    try:
        users = db.getAllUsers()
        if not users:
            print("No users found in the database.")
            return 0

        # Find the maximum length for each column for pretty formatting
        max_id_len = max(len("ID"), max(len(str(user.id)) for user in users))
        max_username_len = max(len("USERNAME"), max(len(user.username) for user in users))
        max_status_len = len("PASSWORD STATUS")

        # Format the header with proper padding
        header = (
            f"{'ID'.ljust(max_id_len)} | "
            f"{'USERNAME'.ljust(max_username_len)} | "
            f"{'PASSWORD STATUS'.ljust(max_status_len)}"
        )

        # Create a separator line
        separator = "-" * (max_id_len + 3 + max_username_len + 3 + max_status_len)

        # Print the header and separator
        print(separator)
        print(header)
        print(separator)

        # Print each user's information
        for user in users:
            status = "Needs change" if user.password_needs_update else "OK"
            user_line = (
                f"{str(user.id).ljust(max_id_len)} | "
                f"{user.username.ljust(max_username_len)} | "
                f"{status.ljust(max_status_len)}"
            )
            print(user_line)

        print(separator)
        print(f"Total: {len(users)} user(s)")
        return 0
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        return 1

class CustomHelpFormatter(argparse.HelpFormatter):
    """Custom help formatter to show full help for all subcommands"""
    pass

def show_full_help(parser, subparsers):
    """Show help for all subcommands"""
    print(parser.format_help())
    print("\nAvailable commands:\n")

    # Iterate through subparsers and print their help
    for choice, subparser in subparsers.choices.items():
        # Add a separator for readability
        print("=" * 60)
        print(f"Command: {choice}")
        print("-" * 60)
        # Format and print the subparser's help
        help_text = subparser.format_help()
        # Remove the usage line which usually contains the program name
        help_lines = help_text.split('\n')
        # Join all lines except the first one (usage)
        print('\n'.join(help_lines[1:]))
        print()

    return 0

def main():
    # Create parser with our custom help formatter
    parser = argparse.ArgumentParser(
        description="Manage users in the SansCoeur database",
        add_help=False  # Disable built-in help
    )

    # Add help argument manually
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message and exit')
    parser.add_argument("--db-path", default="./instance/db.sqlite", help="Path to the database (default: ./instance/db.sqlite)")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.metavar = "COMMAND"  # Makes the help output more readable

    # Add user subcommand
    add_parser = subparsers.add_parser("add", help="Add a new user")
    add_parser.add_argument("username", help="Username to add")
    add_parser.add_argument("--password", help="Password (if not specified, first letter will be used)")
    add_parser.add_argument("--no-force-change", action="store_true", help="Do not force password change on first login")

    # Update password subcommand
    password_parser = subparsers.add_parser("password", help="Update user password")
    password_parser.add_argument("username", help="Username to update")
    password_parser.add_argument("password", help="New password")

    # Update password flag subcommand
    flag_parser = subparsers.add_parser("flag", help="Update user's password change flag")
    flag_parser.add_argument("username", help="Username to update")
    flag_parser.add_argument("--require-change", action="store_true", help="Require password change on next login")
    flag_parser.add_argument("--no-require-change", dest="require_change", action="store_false", help="Don't require password change on next login")
    flag_parser.set_defaults(require_change=True)
    
    # List users subcommand
    list_parser = subparsers.add_parser("list", help="List all users in the database")
    
    # Delete user subcommand
    delete_parser = subparsers.add_parser("delete", help="Delete a user from the database")
    delete_parser.add_argument("username", help="Username to delete")

    # Parse arguments without exiting on help
    args, unknown = parser.parse_known_args()

    # Show full help if --help or -h is specified
    if '-h' in unknown or '--help' in unknown or args.help or not args.command:
        return show_full_help(parser, subparsers)

    # Check if the database path exists
    if not os.path.exists(os.path.dirname(args.db_path)):
        logger.info(f"Creating directory {os.path.dirname(args.db_path)}")
        try:
            os.makedirs(os.path.dirname(args.db_path))
        except Exception as e:
            logger.error(f"Unable to create directory: {e}")
            return 1

    # Initialize the database manager
    try:
        db = dbManager.dbManager(args.db_path)
    except Exception as e:
        logger.error(f"Error initializing the database: {e}")
        return 1

    # Execute the appropriate command
    if args.command == "add":
        return add_user(args, db)
    elif args.command == "password":
        return update_password(args, db)
    elif args.command == "flag":
        return update_password_flag(args, db)
    elif args.command == "list":
        return list_users(args, db)
    elif args.command == "delete":
        return delete_user(args, db)
    else:
        return show_full_help(parser, subparsers)

if __name__ == "__main__":
    sys.exit(main())
