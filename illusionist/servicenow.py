# TODO: to be deprecated in illusionist 3.0. Delete with engine.py.

# temperarily disable impala to work in local
# from python_utils.impala import impala_global


class ServiceNow():

    def find_user(self, name_or_email):
        """
        Find user by their full name, exact match.
        :param name_or_email: match the name_display_value and email_display_value in SN sys_user table.
        :return: (name_display_value, email_display_value).
        here we return 6 so UI know we get more than 5, and ask user to search again.
        """
        # replace multiple space with one space
        name_or_email = ' '.join(name_or_email.split()).lower()

        # sql = """
        #       select name_display_value as name, email_display_value as email
        #       from {}
        #       where lower(name_display_value) like '%{}%' or lower(email_display_value) like '%{}%'
        #       limit 6
        #       """.format(app_config['servicenow']['sys_user_table'], name_or_email, name_or_email)

        # result = impala_global.fetchall(sql, as_dataframe=False)
        result = []
        if not result:
            return []

        users = []
        for user in result:
            user_dict = {
                "name": user[0],
                "email": user[1]
            }
            users.append(user_dict)

        return users
