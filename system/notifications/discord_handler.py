import asyncio
import io
import os
import threading
from typing import Callable

import discord
from dotenv import load_dotenv

load_dotenv()


class AlertView(discord.ui.View):
    def __init__(
        self,
        printer_name: str,
        stop_callback: Callable[[], None],
        allowed_user_id: int,
    ):
        super().__init__(timeout=3600)
        self.printer_name = printer_name
        self.stop_callback = stop_callback
        self.allowed_user_id = allowed_user_id
        self.handled = False
        self.busy = False

    async def interaction_check(self, interaction):
        if interaction.user.id != self.allowed_user_id:
            await interaction.response.send_message(
                "You cannot control this printer.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(
        label="Stop print",
        style=discord.ButtonStyle.danger,
    )
    async def stop(self, interaction, button):
        if self.handled or self.busy:
            await interaction.response.send_message(
                "This alert is already being handled.",
                ephemeral=True,
            )
            return

        self.busy = True
        await interaction.response.defer()

        try:
            # Avoid blocking Discord's event loop
            await asyncio.to_thread(self.stop_callback)
        except Exception:
            self.busy = False
            await interaction.followup.send(
                "Failed to stop the printer. Check its status.",
                ephemeral=True,
            )
            return

        self.handled = True
        self._disable_buttons()
        await interaction.message.edit(view=self)
        await interaction.followup.send(
            f"Stop command sent to {self.printer_name}."
        )
        self.stop()

    @discord.ui.button(
        label="Continue printing",
        style=discord.ButtonStyle.success,
    )
    async def continue_print(self, interaction, button):
        if self.handled or self.busy:
            await interaction.response.send_message(
                "This alert is already being handled.",
                ephemeral=True,
            )
            return

        self.handled = True
        self._disable_buttons()
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(
            f"Alert dismissed for {self.printer_name}."
        )
        self.stop()

    def _disable_buttons(self):
        for button in self.children:
            button.disabled = True


class DiscordHandler(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())

        self.token = os.environ["DISCORD_TOKEN"]
        self.channel_id = int(
            os.environ["DISCORD_CHANNEL_ID"]
        )
        self.allowed_user_id = int(
            os.environ["DISCORD_ALLOWED_USER_ID"]
        )

        self.loop_ref = None

    async def setup_hook(self):
        self.loop_ref = asyncio.get_running_loop()

    def start_background(self):
        thread = threading.Thread(
            target=self.run,
            args=(self.token,),
            daemon=True,
        )
        thread.start()

    async def _send_alert(
        self,
        printer_name: str,
        image_bytes: bytes,
        stop_callback: Callable[[], None],
    ):
        await self.wait_until_ready()

        channel = self.get_channel(self.channel_id)
        if channel is None:
            channel = await self.fetch_channel(
                self.channel_id
            )

        image = discord.File(
            io.BytesIO(image_bytes),
            filename="failure.jpg",
        )

        embed = discord.Embed(
            title="Possible spaghetti failure",
            description=f"Printer: {printer_name}",
            color=discord.Color.red(),
        )
        embed.set_image(
            url="attachment://failure.jpg"
        )

        view = AlertView(
            printer_name,
            stop_callback,
            self.allowed_user_id,
        )

        return await channel.send(
            embed=embed,
            file=image,
            view=view,
        )

    def send_alert(
        self,
        printer_name: str,
        image_bytes: bytes,
        stop_callback: Callable[[], None],
    ):
        if self.loop_ref is None:
            raise RuntimeError("Discord bot not started")

        return asyncio.run_coroutine_threadsafe(
            self._send_alert(
                printer_name,
                image_bytes,
                stop_callback,
            ),
            self.loop_ref,
        )
