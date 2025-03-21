FROM ubuntu:24.04

# Set non-interactive mode for APT
ENV DEBIAN_FRONTEND=noninteractive

# Install system utilities, LaTeX, and Python dependencies
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-venv
RUN apt-get install -y curl
RUN apt-get install -y git
RUN apt-get install -y texlive-full
RUN apt-get install -y dvisvgm
RUN apt-get install -y cairosvg
RUN apt-get install -y sudo
RUN rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -ms /bin/bash latexuser && \
    usermod -aG sudo latexuser && \
    echo "latexuser ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/latexuser

# Set user to latexuser
USER latexuser
WORKDIR /workspaces/latex2image

# Setup Python virtual environment
RUN python3 -m venv /home/latexuser/venv
ENV PATH="/home/latexuser/venv/bin:$PATH"

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pillow cairosvg

# Ensure workspace directory exists
RUN mkdir -p /workspaces/latex2image

# Expose port if needed in the future
EXPOSE 8000